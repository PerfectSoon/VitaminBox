from contextlib import asynccontextmanager
import logging
import uvicorn
import traceback_with_variables

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.create_admin import create_admin_user, seed_database
from app.models.base import Base
from app.database.connection import engine, AsyncSessionLocal

from app.api.v1 import (
    auth_router,
    user_form_router,
    product_router,
    order_router,
    admin_user_router,
    admin_product_router,
    admin_promo_router,
)
from app.exceptions.handler_errors import register_errors_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        try:
            await create_admin_user(session)
            await seed_database(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

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
API_V1_ADMIN = "/api/v1/admin"
app.include_router(
    auth_router, prefix=f"{API_V1}/auth", tags=["Аутентификация"]
)
app.include_router(
    user_form_router, prefix=f"{API_V1}/user_form", tags=["Анкета"]
)
app.include_router(product_router, prefix=f"{API_V1}/product", tags=["Продукт"])
app.include_router(order_router, prefix=f"{API_V1}/order", tags=["Заказ"])
app.include_router(
    admin_user_router,
    prefix=f"{API_V1_ADMIN}/user",
    tags=["Админка: Пользователь"],
)
app.include_router(
    admin_product_router,
    prefix=f"{API_V1_ADMIN}/product",
    tags=["Админка: Продукт"],
)
app.include_router(
    admin_promo_router,
    prefix=f"{API_V1_ADMIN}/promo",
    tags=["Админка: Промокод"],
)

register_errors_handler(app)


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    try:
        uvicorn.run("main:app", reload=True)
    except Exception:
        traceback_with_variables.print_exc()
