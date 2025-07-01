## 🧴 VitaminBoxApp

📦 СТЭК

Python 3.11

FastAPI

SQLAlchemy

Alembic

Docker & Docker Compose

Pytest

Pydantic

PostgreSQL
## 🚀 Установка и запуск через Docker Compose

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/perfect-org/backend.git
   cd VitaminBox
   ```
2. Скопируйте .env:
    ```bash
    cp .env_example .env
   ```
3. Запуск через docker-compose:
    ```bash
    docker-compose up --build -d
   ```
4. Запуск через make:
    ```bash
    make up
   ```
