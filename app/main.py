from contextlib import asynccontextmanager

import uvicorn
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.base import Base
from app.database.connection import engine

from app.api.v1 import (
    auth_router,
    user_form_router,
    product_router,
    admin_user_router,
    admin_product_router,
)
from app.exceptions.handler_errors import register_errors_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="VitaminBox", lifespan=lifespan, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_V1 = "/api/v1"
app.include_router(
    auth_router, prefix=f"{API_V1}/auth", tags=["Аутентификация"]
)
app.include_router(
    user_form_router, prefix=f"{API_V1}/user_form", tags=["Анкета"]
)
app.include_router(product_router, prefix=f"{API_V1}/product", tags=["Продукт"])
app.include_router(
    admin_user_router, prefix=f"{API_V1}/admin", tags=["Админка: Пользователь"]
)
app.include_router(
    admin_product_router, prefix=f"{API_V1}/admin", tags=["Админка: Продукт"]
)

register_errors_handler(app)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    uvicorn.run("main:app", reload=True)
