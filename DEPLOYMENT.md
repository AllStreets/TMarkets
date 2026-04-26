# TMarkets — Deployment Guide

## Prerequisites

- Docker Desktop (Mac/Windows) or Docker Engine + Compose plugin (Linux)
- Git

No Python or Node.js installation required — everything runs inside containers.

---

## Local Development

### 1. Clone

```bash
git clone https://github.com/AllStreets/TMarkets.git
cd TMarkets
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
# Required — data will not load without these
OPENAI_API_KEY=sk-...          # GPT-4.1-mini signal classification
FRED_API_KEY=...               # Federal Reserve macro data
NEWS_API_KEY=...               # Breaking news headlines
GNEWS_API_KEY=...              # Watchlist mover stories

# Optional — daily 7am email brief
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASS=your-app-password    # Gmail → Settings → App Passwords
SMTP_TO=recipient@example.com

# Pre-filled (do not change for local dev)
POSTGRES_URL=postgresql://tmarkets:tmarkets@db:5432/tmarkets
REDIS_URL=redis://redis:6379/0
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Start

```bash
./start.sh
```

This script:
1. Checks `.env` exists
2. Starts PostgreSQL + Redis
3. Polls `pg_isready` until the database accepts connections
4. Runs `alembic upgrade head` to apply migrations
5. Starts the API, Celery worker, Celery Beat, and Next.js frontend

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

### 4. First data load

Workers start polling immediately after launch. Allow 1–2 minutes for:
- Market quotes to populate (yfinance, 5-min cycle)
- Trump signal feed to ingest and classify

Watch logs:

```bash
docker compose logs -f worker
```

---

## Manual Docker Compose Commands

```bash
# Start everything
docker compose up -d

# Stop everything (preserves DB data)
docker compose down

# Stop and wipe the database
docker compose down -v

# Rebuild after code changes
docker compose up -d --build api worker beat frontend

# Apply new migrations
docker compose run --rm api alembic upgrade head

# Create a new migration after model changes
docker compose run --rm api alembic revision --autogenerate -m "add new table"

# Tail logs per service
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f beat
docker compose logs -f frontend
```

---

## Running Backend Tests

```bash
# Using Docker
docker compose run --rm api bash -c "PYTHONPATH=. pytest tests/ -v"

# Or locally (requires Python 3.8+ and installed requirements)
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest tests/ -v
```

---

## Production Deployment

### Option A — Single VPS (DigitalOcean / Hetzner / Linode)

**Recommended spec:** 2 vCPU, 4GB RAM, Ubuntu 22.04

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Clone and configure
git clone https://github.com/AllStreets/TMarkets.git
cd TMarkets
cp .env.example .env
# Edit .env with production values (see below)

# Start
./start.sh
```

**Production `.env` changes:**

```env
# Point to your domain
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com

# Use a strong Postgres password
POSTGRES_URL=postgresql://tmarkets:STRONG_PASSWORD@db:5432/tmarkets
```

**Nginx reverse proxy (port 80/443):**

```nginx
server {
    server_name yourdomain.com;
    location / { proxy_pass http://localhost:3000; }
}

server {
    server_name api.yourdomain.com;
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";  # required for WebSocket
    }
}
```

Obtain SSL with Certbot: `sudo certbot --nginx`

### Option B — Railway / Render / Fly.io

These platforms support Docker Compose via their CLI tools or separate service definitions. Key considerations:

- Set all `.env` variables as platform environment secrets
- Use managed PostgreSQL (Railway Postgres, Render PostgreSQL) — update `POSTGRES_URL`
- Use managed Redis (Railway Redis, Upstash) — update `REDIS_URL`
- Deploy `api`, `worker`, `beat`, and `frontend` as separate services sharing the same env vars

### Option C — AWS ECS / GCP Cloud Run

Use the individual Dockerfiles:

- `backend/Dockerfile` — serves API, worker, and beat (different `command` per task definition)
- `frontend/Dockerfile` — Next.js frontend

Use RDS (Postgres) and ElastiCache (Redis) for managed infra.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `POSTGRES_URL` | Yes | — | PostgreSQL connection string |
| `REDIS_URL` | Yes | — | Redis connection string |
| `OPENAI_API_KEY` | Yes | — | GPT-4.1-mini for signal classification |
| `FRED_API_KEY` | Yes | — | Federal Reserve economic data |
| `NEWS_API_KEY` | Yes | — | NewsAPI.org headlines |
| `GNEWS_API_KEY` | Yes | — | GNews.io headlines |
| `ALPHA_VANTAGE_KEY` | No | — | Reserved for future use |
| `POLYGON_API_KEY` | No | — | Reserved for future use |
| `SMTP_HOST` | No | smtp.gmail.com | Email server host |
| `SMTP_PORT` | No | 587 | Email server port |
| `SMTP_USER` | No | — | Email sender address |
| `SMTP_PASS` | No | — | Email sender password / app password |
| `SMTP_TO` | No | — | Recipient address for daily brief |
| `NEXT_PUBLIC_API_URL` | Yes | http://localhost:8000 | API base URL (browser-visible) |
| `NEXT_PUBLIC_WS_URL` | Yes | ws://localhost:8000 | WebSocket URL (browser-visible) |

---

## Obtaining API Keys

### OpenAI (required)
1. Go to platform.openai.com → API Keys
2. Create a new secret key
3. Ensure your account has access to `gpt-4.1-mini`

### FRED (required)
1. Go to https://fred.stlouisfed.org/docs/api/api_key.html
2. Create a free account and request an API key
3. Approval is instant

### NewsAPI (required)
1. Go to https://newsapi.org → Get API Key
2. Free tier: 100 requests/day — sufficient for development
3. Developer plan ($449/yr) for production volume

### GNews (required)
1. Go to https://gnews.io → Get API Key
2. Free tier: 100 requests/day

### Gmail App Password (optional, for daily brief)
1. Enable 2FA on your Google account
2. Go to Google Account → Security → App Passwords
3. Create a password for "Mail" on "Other device"
4. Use this as `SMTP_PASS` (not your regular Gmail password)

---

## Updating

```bash
git pull
docker compose up -d --build api worker beat frontend
docker compose run --rm api alembic upgrade head
```

---

## Troubleshooting

**Dashboard shows no data after startup**

Workers take 1–2 minutes to complete their first poll cycle. Check:
```bash
docker compose logs -f worker | grep -E "Fetched|ERROR"
```

**WebSocket not connecting**

Ensure `NEXT_PUBLIC_WS_URL` matches your actual API address. In production behind nginx, confirm the WebSocket upgrade headers are forwarded (see nginx config above).

**GPT classification not running**

Check that `OPENAI_API_KEY` is set and the model `gpt-4.1-mini` is available on your account:
```bash
docker compose logs worker | grep -E "openai|GPT|prediction"
```

**Database migration failed**

```bash
docker compose run --rm api alembic history
docker compose run --rm api alembic current
docker compose run --rm api alembic upgrade head
```

**Port already in use**

Change the host port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # use 8001 instead of 8000
```

Then update `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` in `.env` accordingly.
