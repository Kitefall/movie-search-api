import jwt
from authx import AuthX, AuthXConfig
from config import JWTSettings
from database.crud.user_crud import get_user_by_id
from database.database import get_session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from services.log import get_logger
from services.service import SecurityService
from sqlalchemy.ext.asyncio import AsyncSession

settings = JWTSettings()

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = settings.JWT_ACCESS_COOKIE_NAME
config.JWT_COOKIE_SECURE = settings.JWT_COOKIE_SECURE
config.JWT_COOKIE_CSRF_PROTECT = settings.JWT_COOKIE_CSRF_PROTECT
config.JWT_ALGORITHM = settings.JWT_ALGORITHM
security_service = SecurityService()

logger = get_logger(logger_name=__name__)


def get_security_service() -> SecurityService:
    return security_service


security = AuthX(config=config)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
    )
    try:
        payload: dict = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user = await get_user_by_id(session=session, user_id=int(user_id))
        if user is None:
            raise credentials_exception
        return user

    except JWTError as je:
        logger.error("Ошибка JWTError %s", str(je))
        raise credentials_exception
    except Exception as ex:
        logger.error("Непредвиденная ошибка %s", str(ex))
