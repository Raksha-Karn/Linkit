#!/bin/bash
set -e

export DATABASE_URL=$(echo $DATABASE_URL | sed 's/^postgres:/postgresql:/')

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 3