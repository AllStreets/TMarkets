# TMarkets — Design Spec
**Date:** 2026-04-25  
**Status:** Approved for implementation

---

## Overview

TMarkets is a Bloomberg Terminal-style investment dashboard that monitors Trump's statements and actions, classifies their likely market impact using GPT-4.1-mini and a quantitative correlation engine, and delivers autonomous investment recommendations via real-time alerts and a 7am EST daily email brief. All data is cited inline per tile.

---

## Architecture

**Stack:** Next.js 14 (App Router) + Python FastAPI + Celery + Redis + PostgreSQL  
**Orchestration:** Docker Compose (local first, hostable later)

### Services

| Service | Role |
|---|---|
| `frontend` | Next.js dashboard — Bloomberg dark UI, WebSocket client |
| `api` | FastAPI — REST endpoints, WebSocket broadcast, Celery task dispatch |
| `worker` | Celery worker — data ingestion, prediction engine, notification dispatch |
| `beat` | Celery Beat — scheduled jobs (7am brief, periodic data refresh) |
| `redis` | Message broker + result cache |
| `db` | PostgreSQL — market history, signals, predictions, news cache |

---

## Dashboard UI

**Aesthetic:** Bloomberg terminal dark — `#06070d` base, IBM Plex Mono font, cyan/green/red accent system, glowing live indicators, gradient tile backgrounds with top-accent color bars.

**Layout:** Dense grid (Layout B), fully scrollable, not paginated.

### Sections (top to bottom)

1. **Sticky topbar** — logo, live dot, market status, alert count, algo status, next brief countdown
2. **Sticky animated ticker** — 30+ symbols scrolling continuously; Trump alert bursts and AI call bursts interrupt inline; hover to pause; every item clickable
3. **Major Indices** — 6-column grid: SPY, QQQ, DIA, VIX, IWM, DXY; top color accent bar per direction; click opens modal chart
4. **Macro Indicators (FRED)** — 6-column: Fed Funds Rate, CPI YoY, 10Y Yield, Unemployment, GDP Growth, M2 Supply; all cited to FRED
5. **Commodities & Currencies** — 6-column: Gold, WTI, Silver, EUR/USD, USD/CNY, USD/JPY
6. **Trump Signal + AI Recommendation + Sector Heatmap** — 3-column asymmetric row
   - Trump tile: full quote, source, timestamp, classification tag, affected sector tags
   - AI tile: BUY/SHORT call rows with ticker, reason, historical basis; confidence bar
   - Heatmap: 8-sector 2×4 grid, color-coded by performance, each cell clickable
7. **Mega-Cap Watchlist** — 2 rows of 5 sparkline chart tiles; gradient fills; click to expand modal with 30-day chart and OHLCV
8. **Trump Signal History** — split row: left = 5 most recent signals with outcome data; right = accuracy bars by signal type + signal impact distribution bar
9. **International Markets** — 8-column: HSI, Shanghai, Nikkei, DAX, FTSE, CAC, Bovespa, TSX
10. **Options Flow + Earnings Calendar** — split row: unusual options activity (symbol, strike, premium, size); earnings table filtered to Trump-sensitive names with impact rating
11. **Market Breadth & Sentiment** — 4-column: A/D ratio, Fear & Greed index bar, 52-week highs/lows, put/call ratio
12. **News Feed** — 3-column, 4 stories each: Breaking, Policy & Regulation (WH Press), Watchlist Movers; every headline clickable (opens source article in new tab)
13. **Footer** — full data source attribution, algorithm credit, next brief countdown

### Citation System

Every tile displays a `cite` label (7.5px, `#1a2a3a`) listing the specific data source(s). This appears on all tiles without exception.

### Interactivity

- Click any index/macro/commodity tile → modal with expanded chart
- Click any sparkline chart tile → modal with 30-day SVG chart + OHLCV stats
- Click any sector heatmap cell → modal with sector ETF chart
- Click any news headline → opens source article in new tab
- Click any Trump signal history item → modal with full signal detail and algorithm reasoning
- Ticker hover → pauses scroll animation
- Modal dismiss → Escape key or click outside

---

## Data Pipeline

**Framework:** Celery workers pulling from multiple free-tier sources, storing to PostgreSQL with source metadata attached to every record.

### Sources

| Data Type | Source | Refresh Rate |
|---|---|---|
| Stock prices, ETFs | yfinance | Every 5 min (market hours) |
| Additional price data | Alpha Vantage free (25 req/day) | Hourly for key tickers |
| End-of-day + options | Polygon.io free tier | EOD + options flow every 15 min |
| Macro indicators | FRED API | Daily (on data release schedule) |
| News articles | NewsAPI free tier | Every 10 min |
| News articles (backup) | GNews free tier | Every 10 min |
| Trump statements | Truth Social scraper | Every 5 min |
| Trump policy | White House press releases | Every 15 min |
| SEC regulatory filings | SEC EDGAR free API | Daily |

### Storage Schema (PostgreSQL)

- `market_data` — symbol, price, change, volume, timestamp, source
- `trump_signals` — raw_text, source, timestamp, classification, affected_sectors, confidence, prediction_id
- `predictions` — signal_id, buy_list, short_list, reasoning, confidence, horizon_days, outcome (populated later)
- `news_articles` — headline, source, url, published_at, tags
- `macro_data` — indicator, value, period, source, fetched_at

---

## Prediction Algorithm

### Pipeline (per Trump signal detected)

**Step 1 — Signal ingestion**  
Celery worker detects new statement from any monitored source. Deduplication check against `trump_signals` table (fuzzy match on text + 30-min time window).

**Step 2 — GPT-4.1-mini classification**  
System prompt instructs the model to return structured JSON:
```json
{
  "signal_type": "TRADE_TARIFF",
  "affected_tickers": ["AAPL", "AMZN", "FXI"],
  "affected_sectors": ["Technology", "Retail", "Shipping"],
  "directional_bias": {"AAPL": "negative", "GLD": "positive"},
  "reasoning": "...",
  "llm_confidence": 0.87
}
```

**Step 3 — Quant correlation lookup**  
Query `trump_signals` + `market_data` for the 20 most historically similar signals (same signal_type, similar sector tags). Compute average price moves at +1/+3/+5/+7 day intervals. Weight by recency and similarity score.

**Step 4 — Confidence scoring**  
`final_confidence = (llm_confidence * 0.5) + (quant_sample_coverage * 0.3) + (historical_accuracy_for_type * 0.2)`

Where `quant_sample_coverage = min(similar_signals_found, 20) / 20` — scales from 0 (no history) to 1 (full 20-signal sample).  
Threshold: alerts only fire when `final_confidence >= 0.55`.

**Step 5 — Recommendation output**  
Stored to `predictions` table. Pushed to FastAPI WebSocket broadcast channel. Notification system triggered.

---

## Notification System

### Real-time alerts (confidence ≥ 55%)

1. Celery worker writes prediction to DB
2. FastAPI WebSocket broadcasts to all connected dashboard clients
3. Dashboard plays audio chime + displays banner with BUY/SHORT list
4. `osascript` call from worker triggers macOS native notification (works when browser is backgrounded)
5. **Throttle:** max 1 alert per 15-minute window to suppress noise from rapid posting

### 7am EST Daily Brief (Celery Beat)

Runs at `0 12 * * *` UTC (7am EST / UTC-5). Note: adjust to `0 11 * * *` UTC during daylight saving time (EDT / UTC-4), or use `America/New_York` timezone in Celery Beat config to handle automatically. Task:
1. Aggregates overnight signals (midnight–7am)
2. Pulls top movers, biggest sector moves, macro data changes
3. Formats HTML email digest with full citation list
4. Sends via SMTP (user-configurable; off by default until credentials set)

Content of brief:
- Overnight Trump signals + AI calls
- Pre-market movers
- Key macro releases today
- Top options flow from prior session
- High-impact earnings today

---

## Technical Decisions

- **Docker Compose** — all services defined in one `docker-compose.yml`; `docker compose up` starts everything locally
- **WebSockets** — FastAPI native WebSocket support; Next.js client reconnects on disconnect
- **GPT-4.1-mini** — OpenAI SDK; response schema enforced with `response_format: { type: "json_object" }`
- **No auth** — single-user local tool; no login system needed
- **`.gitignore`** — `.superpowers/`, `.env`, `__pycache__/`, `node_modules/`
- **Environment** — all API keys in `.env` file; loaded via `python-dotenv` and Next.js `env.local`

---

## API Keys Required

| Key | Source | Free Tier |
|---|---|---|
| `FRED_API_KEY` | Already have | Yes |
| `OPENAI_API_KEY` | OpenAI | Pay-per-use |
| `ALPHA_VANTAGE_KEY` | alphavantage.co | 25 req/day |
| `POLYGON_API_KEY` | polygon.io | EOD + delayed |
| `NEWS_API_KEY` | newsapi.org | 100 req/day |
| `GNEWS_API_KEY` | gnews.io | 100 req/day |
| `SMTP_*` | Any SMTP provider | Gmail works |

`yfinance`, Truth Social scraper, WH Press, and SEC EDGAR require no API key.

---

## Out of Scope (v1)

- User authentication
- Multi-user support
- Brokerage API integration (actual trade execution)
- Mobile-responsive layout
- Historical charting beyond 30 days on expanded modal
