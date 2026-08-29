from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from services.log import get_logger

logger = get_logger(logger_name=__name__)

home_route = APIRouter(tags=["Home"])


@home_route.get("/")
async def home():
    logger.info("Пользователь перенаправлен на главную страницу")
    return RedirectResponse(url="http://localhost:7860")
