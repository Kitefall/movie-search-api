from decimal import Decimal

from models.coinaccount import CoinAccount
from models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_coin_account(session: AsyncSession,
                              user: User) -> CoinAccount:
    coin_account = CoinAccount()
    user.coin_account = coin_account
    session.add(coin_account)
    return coin_account


async def update_add_coins(session: AsyncSession,
                           user_id: int,
                           amount: Decimal) -> None:
    if amount <= Decimal("0"):
        raise ValueError("Сумма пополнения должна быть положительной")
    sttm = await session.execute(select(CoinAccount).filter(
        CoinAccount.user_id == user_id))
    coin_account = sttm.scalars().first()
    if coin_account is None:
        raise ValueError(f"CoinAccount для user_id={user_id} не найден")
    coin_account.balance += amount
    session.add(coin_account)


async def update_write_off(session: AsyncSession,
                           user_id: int,
                           amount: Decimal) -> None:
    if amount < Decimal("0"):
        raise ValueError("Сумма списания не может быть отрицательна")
    sttm = await session.execute(select(CoinAccount).filter(
        CoinAccount.user_id == user_id))
    coin_account = sttm.scalars().first()
    if coin_account is None:
        raise ValueError(f"CoinAccount для user_id={user_id} не найден")
    if amount > coin_account.balance:
        raise ValueError("Недостаточно средств")
    coin_account.balance -= amount
    session.add(coin_account)


async def get_coin_account_by_id(
        session: AsyncSession,
        user_id: int
):
    sttm = await session.execute(
            select(CoinAccount).where(CoinAccount.user_id == user_id)
    )
    coin_account = sttm.scalars().first()
    return coin_account
