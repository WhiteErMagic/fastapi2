from contextlib import asynccontextmanager
from fastapi import FastAPI
from models import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Start')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    engine.dispose()
    print('Stop')