from decimal import Decimal
from typing import List

from models.history_predict import HistoryPredict
from schemas.history_predict_schema import HistoryPredictBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_history_predict(session: AsyncSession,
                                 history_predict: HistoryPredictBase
                                 ) -> HistoryPredict:
    history_predict_obj = HistoryPredict(
        user_id=history_predict.user_id,
        data=history_predict.data,
        prediction_type=history_predict.prediction_type,
        price=Decimal(history_predict.price)
    )
    session.add(history_predict_obj)
    await session.flush()
    return history_predict_obj


async def get_all_history_predict(session: AsyncSession
                                  ) -> List[HistoryPredict]:
    result = await session.execute(select(HistoryPredict))
    return result.scalars().all()


async def get_history_predict_by_user_id(session: AsyncSession,
                                         user_id: int) -> List[HistoryPredict]:
    result = await session.execute(select(HistoryPredict).filter(
        HistoryPredict.user_id == user_id))
    return result.scalars().all()


async def get_history_predict_by_id(
        session: AsyncSession,
        history_predict_id: int
) -> HistoryPredict:
    result = await session.execute(select(HistoryPredict).where(
        HistoryPredict.id == history_predict_id))
    return result.scalars().one()
