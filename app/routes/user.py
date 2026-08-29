import json
from decimal import Decimal
from typing import Dict

from database.crud.coin_account_crud import get_coin_account_by_id
from database.database import get_session
from dependencies.depend import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from schemas.coin_account_schema import TopUpRequest
from services.log import get_logger
from services.service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

user_route = APIRouter(tags=["User"])
logger = get_logger(logger_name=__name__)


@user_route.post("/top-up")
async def top_up(
    data: TopUpRequest,
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Пополнение баланса пользователем
    """
    if data.amount <= Decimal("0"):
        logger.warning(
            "Попытка пополнения с невалидной суммой %s от пользователя %s",
            data.amount,
            current_user.id,
        )
        raise HTTPException(
            status_code=400, detail="Сумма пополнения должна быть больше нуля"
        )
    try:
        await UserService.add_coins(
            session=session, initiator=current_user, amount=data.amount
        )
        session.add(current_user)
        await session.commit()

        coin_account = await get_coin_account_by_id(
            session=session, user_id=current_user.id
        )
        logger.info(
            "Баланс пользователя %s успешно пополнен на %s",
            current_user.id,
            str(data.amount),
        )
    except Exception as ex:
        logger.error(
            "Ошибика при пополнеии баланса пользователя %s",
            str(ex)
        )

    return {
        "message": f"Баланс успешно пополнен на {str(data.amount)}",
        "new_balance": str(coin_account.balance) if coin_account else None,
    }


@user_route.get("/balance")
async def get_balance(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> Dict[str, str]:
    """
    Просмотр баланса пользователем
    """
    try:
        balance = await UserService.get_balance(
            session=session,
            initiator=current_user
        )
        logger.info(
            "Пользователь %s запросил баланс: %s",
            current_user.id, str(balance)
        )
    except Exception as ex:
        logger.error('Ошибка при просмотре баланса %s',
                     str(ex))
    return {"balance": str(balance)}


@user_route.get("/history-predict")
async def get_predict_history(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Просмотр пользователем истории результатов выдачи модели
    """
    try:
        history = await UserService.get_history_predict_model(
            session=session, initiator=current_user
        )

        result = []
        for item in history:
            if item.result is not None:
                film_ids = json.loads(item.result)
            else:
                film_ids = []
            films = await UserService.get_films_by_ids(session, film_ids)
            result.append(
                {**item.__dict__,
                 "result": [film.model_dump() for film in films]}
            )

        logger.info(
            "Пользователь %s запросил историю предсказаний",
            current_user.id
        )
        return result
    except Exception as ex:
        logger.error("Ошибка при попытке получения истории предсказаний %s",
                     str(ex))


@user_route.get("/history-transaction")
async def get_history_transaction(
    current_user=Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Просмотр пользователем истории транзакций
    """
    try:
        history = await UserService.get_user_transaction(
            session=session, initiator=current_user
        )
        logger.info("Пользователь %s запросил историю транзакций",
                    current_user.id)
        return history
    except Exception as ex:
        logger.error(
            "Ошибка при попытке получения транзакций %s",
            str(ex)
        )
