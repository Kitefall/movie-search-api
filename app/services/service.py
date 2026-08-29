from decimal import Decimal
from typing import List, Optional

from database.crud.coin_account_crud import (create_coin_account,
                                             update_add_coins,
                                             update_write_off)
from database.crud.history_predict_crud import (create_history_predict,
                                                get_history_predict_by_user_id)
from database.crud.transaction_crud import (create_transaction,
                                            get_transaction_by_user_id)
from database.crud.user_crud import (create_user, get_user_by_email,
                                     get_user_with_balance, update_user)
from models.decorators import admin_required
from models.film import Film
from models.history_predict import PredictionType
from models.ml_model import Model
from models.transactions import TransactionType
from models.user import User
from passlib.context import CryptContext
from schemas.film_schema import FilmSchema
from schemas.history_predict_schema import HistoryPredictBase
from schemas.transaction_schema import TransactionBase
from schemas.user_schema import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


class SecurityService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self,
                        plain_password: str,
                        hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)


class UserService:
    @staticmethod
    async def create_user(
        session: AsyncSession,
        user_create: UserCreate,
        security_service: SecurityService,
    ) -> User:
        existing_user = await session.execute(
            User.__table__.select().where(User.email == user_create.email)
        )
        existing_user = existing_user.scalars().first()
        if existing_user:
            raise ValueError("Аккунт уже зарегестрирован на эту почту")
        try:
            hashed_password = security_service.get_password_hash(
                user_create.password)
            user_create.password = hashed_password
            user = await create_user(session, user_create)
            await create_coin_account(session=session, user=user)
            return user
        except Exception as e:
            raise ValueError(f"Ошибка при создании пользователя: {str(e)}")

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user: User,
        user_update: UserUpdate,
        security_service: SecurityService,
    ) -> User:
        if user_update.password is not None:
            user_update.password = security_service.get_password_hash(
                user_update.password
            )
        user = await update_user(session=session,
                                 user=user,
                                 user_update=user_update)
        return user

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
        security_service: SecurityService,
    ) -> Optional[User]:
        user = await get_user_by_email(session=session,
                                       user_email=email)
        if not user:
            return None
        verify = security_service.verify_password(
            plain_password=password, hashed_password=user.password
        )
        if not verify:
            return None
        return user

    @staticmethod
    async def add_coins(
        session: AsyncSession,
        initiator: User,
        amount: Decimal,
        target_user: User = None,
        transaction_type: TransactionType = TransactionType.ADD_COINS,
    ) -> None:
        if target_user is None:
            target_user = initiator

        await update_add_coins(session=session,
                               user_id=target_user.id,
                               amount=amount)
        await create_transaction(
            session=session,
            transaction=TransactionBase(
                initiator_id=initiator.id,
                target_user_id=target_user.id,
                transaction_amount=amount,
                transaction_type=transaction_type,
            ),
        )

    @staticmethod
    async def write_off(
        session: AsyncSession,
        initiator: User,
        amount: Decimal,
        target_user: User = None,
        transaction_type: TransactionType = TransactionType.WRITE_OFF,
    ) -> None:
        if target_user is None:
            target_user = initiator

        await update_write_off(session=session,
                               user_id=target_user.id,
                               amount=amount)
        await create_transaction(
            session=session,
            transaction=TransactionBase(
                initiator_id=initiator.id,
                target_user_id=target_user.id,
                transaction_amount=amount,
                transaction_type=transaction_type,
            ),
        )

    @staticmethod
    async def get_user_transaction(
        session: AsyncSession, initiator: User, target_user: User = None
    ):
        if target_user is None:
            target_user = initiator

        return await get_transaction_by_user_id(session=session,
                                                user_id=target_user.id)

    @staticmethod
    async def get_balance(session: AsyncSession,
                          initiator: User,
                          target_user: User = None):
        if target_user is None:
            target_user = initiator

        user_with_account = await get_user_with_balance(
            session=session,
            user_id=initiator.id)
        if user_with_account is None or user_with_account.coin_account is None:
            return None
        return user_with_account.coin_account.balance

    @staticmethod
    async def get_history_predict_model(
        session: AsyncSession, initiator: User, target_user: User = None
    ):
        if target_user is None:
            target_user = initiator
        history = await get_history_predict_by_user_id(
            session=session, user_id=target_user.id
        )
        return history

    @staticmethod
    async def get_films_by_ids(session: AsyncSession, film_ids: List[int]):
        result = await session.execute(
            select(Film).where(Film.id.in_(film_ids)))
        films = result.scalars().all()
        return [FilmSchema.from_orm(film) for film in films]


class AdminService:
    @staticmethod
    @admin_required
    async def add_coins_to_user(
        session: AsyncSession,
        initiator: User,
        amount: Decimal,
        target_user: User
    ):
        await UserService.add_coins(
            session=session,
            initiator=initiator,
            amount=amount,
            target_user=target_user,
            transaction_type=TransactionType.ADMIN_ADD_COINS,
        )

    @staticmethod
    @admin_required
    async def write_off_to_user(
        session: AsyncSession,
        initiator: User,
        amount: Decimal,
        target_user: User
    ):
        await UserService.write_off(
            session=session,
            initiator=initiator,
            amount=amount,
            target_user=target_user,
            transaction_type=TransactionType.ADMIN_WRITE_OFF,
        )

    @staticmethod
    @admin_required
    async def get_transaction(
        session: AsyncSession, initiator: User, target_user: User
    ):
        if target_user is None:
            raise ValueError('Не указан пользователь')
        return await UserService.get_user_transaction(
            session=session, initiator=initiator, target_user=target_user
        )


class ModelService:
    def __init__(self, model: Model, price: Decimal):
        self.model = model
        self.price = price

    async def input_data(
            self,
            session: AsyncSession,
            user: User,
            text: str
    ):
        if len(text) < 4:
            raise ValueError('Слишком короткий запрос')
        await UserService.write_off(
            session=session,
            initiator=user,
            amount=self.price,
            transaction_type=TransactionType.WRITE_OFF
        )
        history_predict = await create_history_predict(
            session=session,
            history_predict=HistoryPredictBase(
                user_id=user.id,
                data=text,
                result=None,
                prediction_type=PredictionType.MODEL_SEND_REQUEST,
                price=Decimal(self.price)
            )
        )
        return history_predict
