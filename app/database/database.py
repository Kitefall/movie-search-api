import pandas as pd
from models.base import Base
from models.film import Film
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .database_config import get_settings

engine = create_async_engine(get_settings().DATABASE_URL_asyncpg, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def load_csv_to_db(csv_path):

    df = pd.read_csv(csv_path)
    records = df.to_dict(orient='records')
    films = [Film(
        **{k: v for k, v in row.items() if k in ['title', 'plot', 'genre']}
        ) for row in records]
    async with AsyncSessionLocal() as session:
        session.add_all(films)
        await session.commit()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    await load_csv_to_db("database/my_data.csv")
