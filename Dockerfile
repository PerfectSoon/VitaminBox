FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

COPY . .

CMD ["/bin/sh", "-c", "/app/wait-for-it.sh uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
