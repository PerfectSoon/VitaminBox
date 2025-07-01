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


async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture()
async def client():
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()  #


@pytest.fixture
async def token_headers(client):
    register_data = {
        "email": "token2@example.com",
        "name": "asdasdm",
        "password": "supersecret",
        "role": "user",
    }
    register_response = await client.post(
        "/api/v1/auth/register", json=register_data
    )
    assert register_response.status_code == 201, "Пользователь не создан!"

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "token2@example.com", "password": "supersecret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    print("Login response:", login_response.json())  # Для отладки
    assert login_response.status_code == 200, "Ошибка авторизации!"
    assert "access_token" in login_response.json(), "Токен не получен!"

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
