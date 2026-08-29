from typing import List

from models.transactions import Transaction
from schemas.transaction_schema import TransactionBase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_transaction_by_id(session: AsyncSession,
                                transaction_id: int) -> List[Transaction]:
    result = await session.execute(select(Transaction).filter(
        Transaction.id == transaction_id))
    return result.scalars().all()


async def get_transaction_by_user_id(session: AsyncSession,
                                     user_id: int) -> List[Transaction]:
    result = await session.execute(select(Transaction).filter(
        Transaction.target_user_id == user_id))
    return result.scalars().all()


async def get_all_transaction(session: AsyncSession) -> List[Transaction]:
    result = await session.execute(select(Transaction))
    return result.scalars().all()


async def create_transaction(session: AsyncSession,
                             transaction: TransactionBase) -> Transaction:
    transaction_obj = Transaction(
        transaction_type=transaction.transaction_type,
        initiator_id=transaction.initiator_id,
        target_user_id=transaction.target_user_id,
        transaction_amount=transaction.transaction_amount
    )
    session.add(transaction_obj)
    return transaction_obj
