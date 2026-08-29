from contextlib import asynccontextmanager

import uvicorn
from database.database import AsyncSessionLocal, get_settings, init_db
from fastapi import FastAPI
from models.user import Role
from routes.admin import admin_route
from routes.auth import auth_route
from routes.home import home_route
from routes.model import broker, model_route, request_queue, response_queue
from routes.user import user_route
from schemas.user_schema import UserCreate
from services.service import SecurityService, UserService

app = FastAPI()

app.include_router(home_route)
app.include_router(model_route, prefix='/model')
app.include_router(user_route, prefix='/user')
app.include_router(auth_route, prefix='/auth')
app.include_router(admin_route, prefix='/admin')

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()

    async with AsyncSessionLocal() as session:
        user_create = UserCreate(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )

        user = await UserService.create_user(
            session=session,
            user_create=user_create,
            security_service=SecurityService()
        )

        user.role = Role.ADMIN
        session.add(user)
        await session.commit()

        await broker.start()
        await broker.declare_queue(request_queue)
        await broker.declare_queue(response_queue)

        yield

        await broker.stop()

app.router.lifespan_context = lifespan

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)
