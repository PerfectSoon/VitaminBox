#!/bin/sh
set -e

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
  echo "Postgres не готов, жду..."
  sleep 2
done

echo "Postgres готов — запускаю приложение"
exec "$@"