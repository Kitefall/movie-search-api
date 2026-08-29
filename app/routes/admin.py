from decimal import Decimal
from typing import Dict, List, Optional

from database.crud.user_crud import get_user_by_id
from database.database import get_session
from dependencies.depend import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from models.user import Role, User
from schemas.admin_schema import AdminCoinsSchema, AdminGetTransactionSchema
from schemas.transaction_schema import TransactionBase
from services.log import get_logger
from services.service import AdminService
from sqlalchemy.orm import Session

admin_route = APIRouter(tags=['Admin'])
logger = get_logger(logger_name=__name__)


@admin_route.post('/top-up')
async def add_coins_to_user(
    schema: AdminCoinsSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Пополнение администратором баланса пользователю
    """
    if current_user.role != Role.ADMIN:
        logger.warning('Доступ запрещен для пользователя: %s', current_user.id)
        raise HTTPException(status_code=403, detail='Доступ запрещен')

    target_user = await get_user_by_id(session=session,
                                       user_id=schema.target_user_id)
    if target_user is None:
        logger.error('Пользователь не найден: %s', schema.target_user_id)
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    await AdminService.add_coins_to_user(session=session,
                                         initiator=current_user,
                                         amount=Decimal(schema.amount),
                                         target_user=target_user)
    await session.commit()
    logger.info('Пополнение баланса: пользователь id = %s, сумма = %s',
                schema.target_user_id, schema.amount)

    return {
        'Успешное пополнение': f'Пользователь id = {schema.target_user_id}',
        'Сумма': str(schema.amount)
    }


@admin_route.post('/write-off')
async def write_off_to_user(
    schema: AdminCoinsSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, str]:
    """
    Списание администратором денег со счета пользователя
    """
    if current_user.role != Role.ADMIN:
        logger.warning('Доступ запрещен для пользователя: %s', current_user.id)
        raise HTTPException(status_code=403, detail='Доступ запрещен')
    try:
        target_user = await get_user_by_id(session=session,
                                           user_id=schema.target_user_id)
        if target_user is None:
            logger.error('Пользователь не найден: %s', schema.target_user_id)
            raise HTTPException(status_code=404,
                                detail="Пользователь не найден")

        await AdminService.write_off_to_user(session=session,
                                             initiator=current_user,
                                             amount=Decimal(schema.amount),
                                             target_user=target_user)
        await session.commit()
        logger.info('Списание баланса: пользователь id = %s, сумма = %s',
                    schema.target_user_id, schema.amount)

        return {
            'Успешное списание': f'Пользователь id = {schema.target_user_id}',
            'Сумма': str(schema.amount)
        }
    except Exception as ex:
        logger.error(
            "Ошибка при попытке списания %s",
            str(ex)
        )


@admin_route.post('/user-transaction')
async def get_transaction_to_user(
    schema: AdminGetTransactionSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Optional[List[TransactionBase]]:
    """
    Просмотр администратором транзакций пользователя
    """
    if current_user.role != Role.ADMIN:
        logger.warning('Доступ запрещен для пользователя: %s', current_user.id)
        raise HTTPException(status_code=403, detail='Доступ запрещен')

    target_user = await get_user_by_id(session=session,
                                       user_id=schema.target_user_id)
    if target_user is None:
        logger.error('Пользователь не найден: %s', schema.target_user_id)
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    try:
        transactions = await AdminService.get_transaction(
            session=session,
            initiator=current_user,
            target_user=target_user
        )
        logger.info('Получение транзакций для пользователя id = %s',
                    schema.target_user_id)

        return transactions
    except Exception as ex:
        logger.error(
            "Ошибка при попытке пополнения %s",
            str(ex)
        )
