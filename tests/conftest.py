import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from httpx import AsyncClient

from app.core.settings import Settings
from app.main import app
from app.models.base import Base
from app.database.connection import get_db  #

settings = Settings()

engine_test = create_async_engine(
    settings.TEST_DB_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, class_=AsyncSession
)


# Переопределение зависимости FastAPI
async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session


# Создание схемы БД один раз перед всеми тестами
@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Сессия на каждый тест
@pytest.fixture(scope="function")
async def db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session  # Можно добавить rollback тут при необходимости


# HTTP-клиент с переопределённой зависимостью
@pytest.fixture()
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()  # Убираем переопределения после теста


# Авторизационные заголовки (регистрация и вход)
@pytest.fixture
async def token_headers(client):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "token@example.com",
            "password": "supersecret",
            "role": "user",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "token@example.com", "password": "supersecret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
