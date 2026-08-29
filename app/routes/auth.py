from typing import Dict

from database.database import get_session
from dependencies.depend import get_security_service, security
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas.user_schema import UserCreate
from services.log import get_logger
from services.service import SecurityService, UserService
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(logger_name=__name__)

auth_route = APIRouter(tags=["Auth"])


@auth_route.post("/signup")
async def signup(
    creds: UserCreate,
    session: AsyncSession = Depends(get_session),
    security_service: SecurityService = Depends(get_security_service),
) -> Dict[str, str]:
    """
    Регистрация пользователя
    """
    try:
        await UserService.create_user(
            session=session,
            user_create=creds,
            security_service=security_service
        )
        await session.commit()
        logger.info("Пользователь успешно создан: %s", creds.email)
    except ValueError as ve:
        logger.warning("Ошибка при регистрации пользователя: %s", str(ve))
        raise HTTPException(
            status_code=422,
            detail=str(ve)
        )
    except Exception as e:
        logger.error("Ошибка на сервере при регистрации: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка на сервере: {str(e)}"
        )
    return {"message": "Пользователь успешно создан"}


@auth_route.post("/signin")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    security_service: SecurityService = Depends(get_security_service),
) -> Dict[str, str]:
    """
    Получение токена
    """
    user = await UserService.authenticate_user(
        session=session,
        email=form_data.username,
        password=form_data.password,
        security_service=security_service
    )
    if not user:
        logger.warning("Неверный логин или пароль для пользователя: %s",
                       form_data.username)
        raise HTTPException(status_code=401,
                            detail="Неверный логин или пароль")
    role_str = user.role.value if hasattr(user.role, "value") else str(
        user.role)
    token = security.create_access_token(uid=str(user.id),
                                         data={"role": role_str})
    logger.info("Пользователь %s вошел в систему", form_data.username)
    return {"access_token": token, "token_type": "bearer"}
