from decimal import Decimal
from typing import Dict

from config import ModelSettings, RabbitmqSettings
from database.database import get_session
from dependencies.depend import get_current_user
from fastapi import Depends, HTTPException
from faststream.rabbit import RabbitBroker, RabbitMessage, RabbitQueue
from faststream.rabbit.fastapi import RabbitRouter
from models.history_predict import HistoryPredict, PredictionType
from models.ml_model import Model
from models.transactions import TransactionType
from models.user import User
from schemas.history_predict_schema import HistoryPredictMessage
from schemas.use_model_schema import InputDataModel
from services.log import get_logger
from services.service import ModelService, UserService
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(logger_name=__name__)

settings = RabbitmqSettings()
model_settings = ModelSettings()

model_route = RabbitRouter(url=settings.RABBITMQ_URL, tags=['Model'])

model = Model("Рекомандация фильмов", "Предложить фильмы по похожим описаниям")
model_service = ModelService(model=model, price=model_settings.MODEL_PRICE)

broker = RabbitBroker(settings.RABBITMQ_URL)

request_queue = RabbitQueue(
    settings.REQUEST_QUEUE,
    durable=True,
    auto_delete=False
)

response_queue = RabbitQueue(
    settings.RESPONSE_QUEUE,
    durable=True,
    auto_delete=False
)


@model_route.post("/data-input")
async def model_input_data(
    data: InputDataModel,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    try:
        text = data.data
        history = await model_service.input_data(
            session=session,
            user=current_user,
            text=text
        )
        history_predict = HistoryPredictMessage(
            id=history.id,
            user_id=current_user.id,
            data=text,
            result=None,
            prediction_type=PredictionType.MODEL_SEND_REQUEST,
            price=model_service.price,
            status=None
        )
        await session.commit()
        await broker.publish(
            message=history_predict,
            queue=request_queue
        )
        logger.info("Запрос успешно отправлен для пользователя %s",
                    current_user.id)
    except ValueError as ve:
        logger.warning("Ошибка: %s для пользователя %s", str(ve),
                       current_user.id)
        if str(ve) == 'Недостаточно средств':
            raise HTTPException(
                status_code=422,
                detail='Недостаточно средств'
            )
        elif str(ve) == 'Слишком короткий запрос':
            raise HTTPException(
                status_code=422,
                detail='Запрос должен быть не менее 4 символов'
            )
        else:
            logger.error("Неизвестная ошибка: %s", str(ve))
            raise HTTPException(
                status_code=500,
                detail="Ошибка на сервере"
            )
    except Exception as e:
        logger.error("Неожиданная ошибка: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Ошибка на сервере"
        )
    return {"Запрос успешно отправлен": "ok"}


@broker.subscriber(
    response_queue,
    no_ack=True
)
async def handle_model_result(
    msg: RabbitMessage,
    data: HistoryPredictMessage
):
    async for session in get_session():
        history: HistoryPredict = await session.get(
            HistoryPredict,
            int(data.id)
        )
        if history:
            history.result = data.result
            if data.status == "True":
                history.prediction_type = PredictionType.MODEL_RECEIVED_PREDICT
            else:
                history.prediction_type = PredictionType.MODEL_ERROR
                user: User = await session.get(
                    User,
                    int(data.user_id)
                )
                await UserService.add_coins(
                    session=session,
                    initiator=user,
                    amount=Decimal(data.price),
                    transaction_type=TransactionType.BACK_COINS
                )
            await session.commit()
            logger.info("Результат модели обработан для истории %s",
                        history.id)
    await msg.ack()
