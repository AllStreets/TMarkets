#!/bin/bash
set -e
echo "Starting TMarkets..."
if [ ! -f .env ]; then
  echo "ERROR: .env not found. Copy .env.example to .env and fill in your API keys."
  exit 1
fi
docker compose up -d db redis
echo "Waiting for PostgreSQL..."
sleep 3
docker compose run --rm api alembic upgrade head
docker compose up -d api worker beat frontend
echo ""
echo "TMarkets running:"
echo "  Dashboard: http://localhost:3000"
echo "  API:       http://localhost:8000"
echo "  API docs:  http://localhost:8000/docs"
