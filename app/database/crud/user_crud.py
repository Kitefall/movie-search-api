from typing import Optional

from models.user import User
from schemas.user_schema import UserCreate, UserUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_user_by_id(session: AsyncSession,
                         user_id: int) -> Optional[User]:
    result = await session.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession,
                            user_email: str) -> Optional[User]:
    result = await session.execute(select(User).filter(
        User.email == user_email))
    return result.scalars().first()


async def get_user_with_balance(
        session: AsyncSession,
        user_id: int
) -> User:
    stmt = (
            select(User)
            .options(selectinload(User.coin_account))
            .where(User.id == user_id)
        )
    result = await session.execute(stmt)
    user_with_account = result.scalars().first()
    return user_with_account


async def create_user(session: AsyncSession,
                      user_create: UserCreate) -> User:
    user = User(
        name=user_create.name,
        email=user_create.email,
        password=user_create.password
    )
    session.add(user)
    return user


async def update_user(session: AsyncSession,
                      user: User,
                      user_update: UserUpdate) -> User:
    update_dict = user_update.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
    return user


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
