from decimal import Decimal

import pytest_asyncio
from api import app
from database.database import get_session
from dependencies.depend import get_current_user
from httpx import ASGITransport, AsyncClient
from models.base import Base
from models.coinaccount import CoinAccount
from models.user import Role
from schemas.user_schema import UserCreate
from services.service import SecurityService, UserService
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///testing.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
async def session():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal(bind=connection) as session:
            try:
                yield session
            finally:
                await session.close()
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def user(session):
    user = await UserService.create_user(
        session=session,
        user_create=UserCreate(
            name='test_user',
            email='test@example.com',
            password='Password1'
        ),
        security_service=SecurityService())
    session.add(user)
    await session.commit()
    yield user


@pytest_asyncio.fixture
async def user_with_balance(session, user):
    await session.execute(
        update(CoinAccount).
        where(CoinAccount.user_id == user.id).
        values(balance=Decimal(5))
    )
    await session.commit()
    await session.refresh(user, attribute_names=['coin_account'])
    yield user


@pytest_asyncio.fixture
async def client(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authorized_client(client, user):
    def get_test_user():
        return user

    app.dependency_overrides[get_current_user] = get_test_user
    yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session")
async def admin_user(session):
    admin_user = await UserService.create_user(
        session=session,
        user_create=UserCreate(
            name='test_user',
            email='test_admin@example.com',
            password='Password1'
        ),
        security_service=SecurityService())
    admin_user.role = Role.ADMIN
    session.add(admin_user)
    await session.commit()
    await session.refresh(admin_user)

    yield admin_user


@pytest_asyncio.fixture(name='admin')
async def authorized_admin_client(client, admin_user):
    def get_test_admin():
        return admin_user

    app.dependency_overrides[get_current_user] = get_test_admin
    yield client
    app.dependency_overrides.clear()
