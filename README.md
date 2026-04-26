# TMarkets

**Bloomberg Terminal-style investment dashboard that monitors Trump's statements, classifies their market impact with GPT-4.1-mini, and delivers autonomous buy/short recommendations via real-time WebSocket alerts and a 7am daily email brief.**

---

## Screenshots

> Dashboard renders in a Bloomberg dark theme — IBM Plex Mono, `#06070d` background, cyan/green/red accent palette.

| Section | Description |
|---|---|
| Topbar + Ticker | Live EST clock, alert count, scrolling price ticker with Trump signal injections |
| Major Indices | SPY, QQQ, DIA, VIX, IWM, DXY tiles with change indicators |
| Macro Panel | Fed Funds, CPI, 10Y Treasury, Unemployment, GDP, M2 — sourced from FRED |
| Trump Signal | Real-time feed from Truth Social, WH Press, NewsAPI — classified by GPT-4.1-mini |
| AI Recommendation | BUY/SHORT list with confidence bar and horizon |
| Sector Heatmap | 8 GICS sectors via ETF proxies (XLK, XLE, XLY, XAR, SOXX, XLB, XLF, XLU) |
| Chart Tiles | Mega-cap watchlist with sparklines — click to expand modal |
| Signal History | Last 5 Trump signals + accuracy bars by signal type |
| International | HSI, Shanghai, Nikkei, DAX, FTSE, CAC, Bovespa, TSX |
| News Feed | 3-column: Breaking / Policy / Watchlist Movers — click to open source |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         TMarkets v1                             │
├──────────────┬──────────────────────────────┬───────────────────┤
│   Frontend   │          Backend             │   Infrastructure  │
│  Next.js 14  │       FastAPI + Celery       │  PostgreSQL Redis │
│  TypeScript  │       Python 3.8.8           │  Docker Compose   │
└──────┬───────┴──────────┬───────────────────┴────────┬──────────┘
       │                  │                             │
       │  REST + WebSocket│                             │
       │◄─────────────────┤                             │
       │                  │   Celery Beat (scheduler)   │
       │                  │◄────────────────────────────┤
       │                  │                             │
       │  WS push via     │   Workers poll & ingest:    │
       │  Redis Pub/Sub   │   • yfinance (5min)         │
       │◄─────────────────┤   • Truth Social / WH Press │
                          │   • FRED macro (6:30am)     │
                          │   • NewsAPI / GNews (10min) │
                          │   • Options flow (15min)    │
                          │   • Daily brief (7am EST)   │
                          │                             │
                          │   GPT-4.1-mini pipeline:    │
                          │   Signal → Classify →       │
                          │   Confidence → BUY/SHORT    │
```

### Signal Pipeline

```
Trump Post / WH Statement / News
          │
          ▼
  Dedup (85% similarity, 24h window)
          │
          ▼
  GPT-4.1-mini Classification
  {signal_type, affected_tickers,
   affected_sectors, confidence, reasoning}
          │
          ▼
  Confidence Formula:
  (llm_conf × 0.5) + (similar_signals/20 × 0.3) + (historical_accuracy × 0.2)
          │
      ≥ 0.55?
         / \
       yes   no → skip
        │
        ▼
  build_recommendation() → BUY list + SHORT list
        │
        ▼
  DB commit → Redis publish → WebSocket broadcast → macOS notification
```

### Historical Accuracy by Signal Type

| Signal Type | Accuracy |
|---|---|
| TRADE_TARIFF | 84% |
| FED_PRESSURE | 79% |
| ENERGY_POLICY | 76% |
| SANCTIONS | 72% |
| INTL_POLICY | 68% |
| DEREGULATION | 65% |
| FISCAL_POLICY | 61% |
| OTHER | 55% |

---

## Data Structure

```
TMarkets/
├── start.sh                          # One-command startup
├── docker-compose.yml                # 6 services: db, redis, api, worker, beat, frontend
├── .env.example                      # API key template
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py # DB schema migration
│   │
│   └── app/
│       ├── config.py                 # Pydantic settings (env vars)
│       ├── database.py               # SQLAlchemy engine + session
│       ├── models.py                 # ORM models
│       ├── schemas.py                # Pydantic response schemas
│       ├── main.py                   # FastAPI app + Redis subscriber + WebSocket
│       ├── websocket.py              # ConnectionManager (broadcast)
│       │
│       ├── routers/
│       │   ├── market.py             # GET /api/market/quotes
│       │   ├── signals.py            # GET /api/signals/latest|history
│       │   ├── predictions.py        # GET /api/predictions/latest
│       │   └── news.py               # GET /api/news/feed
│       │
│       ├── services/
│       │   ├── prediction.py         # GPT-4.1-mini pipeline (Celery task)
│       │   ├── notifications.py      # macOS notification + Redis pub
│       │   └── email_service.py      # 7am HTML brief builder + SMTP sender
│       │
│       └── workers/
│           ├── celery_app.py         # Celery app + Beat schedule
│           ├── market_data.py        # yfinance polling (36 symbols, 5min)
│           ├── trump_signals.py      # Truth Social + WH Press + NewsAPI ingestion
│           ├── macro_data.py         # FRED series (6:30am daily)
│           ├── news_feed.py          # NewsAPI + GNews (10min)
│           ├── options_flow.py       # Options chain scraper (15min)
│           └── daily_brief.py        # 7am email brief builder
│
└── frontend/
    ├── Dockerfile
    ├── next.config.mjs
    ├── public/
    │   └── chime.mp3                 # Alert sound
    │
    └── src/
        ├── app/
        │   ├── globals.css           # Bloomberg dark theme + grid classes
        │   ├── layout.tsx
        │   └── page.tsx              # Full dashboard (wired)
        │
        ├── components/
        │   ├── layout/
        │   │   ├── Topbar.tsx        # Sticky header, clock, alert count
        │   │   ├── Ticker.tsx        # Scrolling price + alert injections
        │   │   └── Footer.tsx        # Data sources + next brief countdown
        │   │
        │   ├── tiles/
        │   │   ├── IndexTile.tsx     # Quote tile with colored top bar
        │   │   ├── MacroTile.tsx     # FRED macro indicator tile
        │   │   ├── ChartTile.tsx     # Quote + sparkline, click to expand
        │   │   ├── HeatmapTile.tsx   # 8-sector green/red heatmap
        │   │   └── NewsTile.tsx      # Clickable news headlines
        │   │
        │   ├── panels/
        │   │   ├── TrumpSignalPanel.tsx      # Live signal feed with sector tags
        │   │   ├── AIRecommendationPanel.tsx # BUY/SHORT + confidence bar
        │   │   └── SignalHistoryPanel.tsx     # Last 5 signals + accuracy bars
        │   │
        │   ├── modals/
        │   │   ├── ChartModal.tsx            # Expanded sparkline + OHLV
        │   │   └── SignalDetailModal.tsx      # Signal + AI reasoning + trades
        │   │
        │   └── shared/
        │       ├── Sparkline.tsx             # SVG sparkline with gradient fill
        │       ├── AlertBanner.tsx           # Fixed toast, auto-dismiss 12s
        │       └── CiteBadge.tsx             # Data source attribution
        │
        ├── hooks/
        │   ├── useMarketData.ts      # Polls all 5 API endpoints (60s)
        │   └── useWebSocket.ts       # Auto-reconnecting WebSocket (3s backoff)
        │
        └── lib/
            ├── api.ts                # Typed fetch wrapper (revalidate: 30s)
            └── types.ts              # Quote, TrumpSignal, Prediction, AlertPayload
```

### Database Schema

```
┌─────────────────────────┐     ┌──────────────────────────────────┐
│       market_data        │     │           trump_signals           │
├─────────────────────────┤     ├──────────────────────────────────┤
│ id          SERIAL PK   │     │ id             SERIAL PK         │
│ symbol      VARCHAR(20)  │     │ raw_text       TEXT              │
│ price       FLOAT        │     │ source         VARCHAR(100)      │
│ change_pct  FLOAT        │     │ signal_type    VARCHAR(50) NULL  │
│ volume      FLOAT NULL   │     │ confidence     FLOAT NULL        │
│ source      VARCHAR(50)  │     │ affected_tickers JSON NULL       │
│ fetched_at  TIMESTAMP    │     │ affected_sectors JSON NULL       │
└─────────────────────────┘     │ llm_reasoning  TEXT NULL         │
                                 │ posted_at      TIMESTAMP         │
┌─────────────────────────┐     └──────────────┬───────────────────┘
│      news_articles       │                    │
├─────────────────────────┤                    │ 1:1
│ id           SERIAL PK  │     ┌──────────────▼───────────────────┐
│ headline     TEXT        │     │           predictions             │
│ url          TEXT        │     ├──────────────────────────────────┤
│ source       VARCHAR     │     │ id           SERIAL PK           │
│ published_at TIMESTAMP   │     │ signal_id    FK → trump_signals  │
│ tags         JSON NULL   │     │ buy_list     JSON                │
└─────────────────────────┘     │ short_list   JSON                │
                                 │ reasoning    TEXT                │
                                 │ confidence   FLOAT               │
                                 │ horizon_days INT                 │
                                 │ created_at   TIMESTAMP           │
                                 └──────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, IBM Plex Mono |
| Backend | FastAPI, Python 3.8.8, Uvicorn |
| Task Queue | Celery 5, Celery Beat, Redis |
| Database | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| AI | GPT-4.1-mini (OpenAI) |
| Market Data | yfinance (36 symbols), FRED API |
| News | NewsAPI, GNews, WH Press RSS, Truth Social |
| Options | yfinance options chain |
| Realtime | WebSocket (FastAPI), Redis Pub/Sub |
| Notifications | macOS `osascript`, SMTP email |
| Infrastructure | Docker Compose |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/api/market/quotes` | Latest quote per symbol |
| GET | `/api/signals/latest` | Most recent Trump signal |
| GET | `/api/signals/history?limit=10` | Signal history |
| GET | `/api/predictions/latest` | Latest AI recommendation |
| GET | `/api/news/feed?limit=30` | Recent news articles |
| WS | `/ws` | Real-time alert stream |

---

## Beat Schedule

| Task | Interval | Description |
|---|---|---|
| `fetch_quotes_task` | 5 min | Poll yfinance for 36 symbols |
| `fetch_trump_signals_task` | 5 min | Ingest + classify new signals |
| `fetch_news_task` | 10 min | Pull NewsAPI + GNews |
| `fetch_options_task` | 15 min | Options chain for watchlist |
| `fetch_macro_task` | Daily 6:30am | FRED economic series |
| `send_daily_brief_task` | Daily 7:00am | Compile + email morning brief |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/AllStreets/TMarkets.git
cd TMarkets

# 2. Configure
cp .env.example .env
# Fill in your API keys (see Deployment Guide below)

# 3. Launch
./start.sh
```

Open **http://localhost:3002**

---

## Required API Keys

| Key | Where to get |
|---|---|
| `OPENAI_API_KEY` | platform.openai.com |
| `FRED_API_KEY` | fred.stlouisfed.org/docs/api/api_key |
| `NEWS_API_KEY` | newsapi.org |
| `GNEWS_API_KEY` | gnews.io |
| `SMTP_*` | Gmail app password (optional — daily brief) |

`ALPHA_VANTAGE_KEY` and `POLYGON_API_KEY` are reserved for future use.

---

## Tests

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
# 21 tests, 0 failures
```

---

## License

MIT
