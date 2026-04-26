from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta
import random

# Must be set before app imports
os.environ.setdefault("POSTGRES_URL", os.getenv("POSTGRES_URL", "postgresql://tmarkets:tmarkets@localhost:5432/tmarkets"))
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.database import SessionLocal, Base, engine
from app.models import MarketData, TrumpSignal, Prediction, NewsArticle

Base.metadata.create_all(bind=engine)
db = SessionLocal()

now = datetime.utcnow()

# ── Market Data ────────────────────────────────────────────────────────────────
QUOTES = [
    ("SPY",   541.28,  1.24,  88_000_000),
    ("QQQ",   461.83,  1.61,  45_000_000),
    ("DIA",   397.44, -0.31,  12_000_000),
    ("^VIX",   16.42, -8.21,         None),
    ("IWM",   197.51,  0.88,  32_000_000),
    ("DX-Y.NYB", 104.12, -0.44,      None),
    ("AAPL",  213.49,  2.11,  55_000_000),
    ("NVDA",  881.40,  3.72, 120_000_000),
    ("TSLA",  247.10, -1.83,  78_000_000),
    ("MSFT",  421.35,  1.09,  22_000_000),
    ("META",  527.80,  2.44,  18_000_000),
    ("AMZN",  195.60,  0.77,  31_000_000),
    ("GLD",   233.50,  0.62,   9_000_000),
    ("TLT",    92.14, -0.55,  14_000_000),
    ("XAR",   141.20,  1.88,   1_200_000),
    ("BTC-USD", 94_211.00, 2.33,      None),
    ("GC=F",  2388.40,  0.51,        None),
    ("CL=F",    83.12, -1.20,        None),
    ("SI=F",    28.44,  0.87,        None),
    ("EURUSD=X", 1.0731, -0.22,      None),
    ("CNY=X",   7.2441,  0.05,       None),
    ("JPY=X",  151.88,  0.31,        None),
    ("XLK",   212.30,  1.71,   5_000_000),
    ("XLE",    88.42, -0.94,   8_000_000),
    ("XLY",   191.10,  0.63,   3_000_000),
    ("SOXX",  214.50,  2.88,   2_000_000),
    ("XLB",    87.34,  0.41,   2_500_000),
    ("XLF",    44.21,  0.55,  12_000_000),
    ("XLU",    68.90, -0.28,   3_000_000),
    ("^HSI",  18_420.0, -0.88,        None),
    ("000001.SS", 3_088.0, 0.32,      None),
    ("^N225", 38_150.0,  1.14,        None),
    ("^GDAXI", 18_240.0,  0.73,       None),
    ("^FTSE",  8_102.0,  0.21,        None),
    ("^FCHI",  8_011.0,  0.44,        None),
    ("BVSP",  128_400.0, -0.61,       None),
    ("GSPTSE", 24_100.0,  0.38,       None),
]

print(f"Seeding {len(QUOTES)} market quotes...")
for sym, price, chg, vol in QUOTES:
    db.add(MarketData(symbol=sym, price=price, change_pct=chg, volume=vol,
                      source="yfinance", fetched_at=now))
db.commit()

# ── Trump Signals ──────────────────────────────────────────────────────────────
SIGNALS = [
    {
        "raw_text": "We are raising tariffs on ALL Chinese imports to 145%. This is just the beginning. China has been ripping us off for years and we are DONE letting it happen. Buy American!",
        "source": "truth_social",
        "signal_type": "TRADE_TARIFF",
        "confidence": 0.91,
        "affected_tickers": ["AAPL", "NVDA", "TSLA", "AMZN"],
        "affected_sectors": ["Technology", "Consumer Disc", "Semis"],
        "llm_reasoning": "Broad tariff announcement with high specificity (145% rate). Historically highest-confidence signal type. Technology and semiconductor supply chains most exposed. Gold as safe haven beneficiary.",
        "offset_hours": 2,
    },
    {
        "raw_text": "Just spoke with President Xi. We had a GREAT call. Trade deals are happening. Markets should be very happy. Stay tuned — BIG announcement coming next week!",
        "source": "truth_social",
        "signal_type": "INTL_POLICY",
        "confidence": 0.72,
        "affected_tickers": ["SPY", "QQQ", "FXI"],
        "affected_sectors": ["Technology", "Materials", "Financials"],
        "llm_reasoning": "Vague positive signal on US-China relations. Limited specificity reduces confidence. Risk-on tone suggests broad equity upside. Wait for actual deal announcement for higher conviction.",
        "offset_hours": 18,
    },
    {
        "raw_text": "The Federal Reserve has NO IDEA what they're doing. Interest rates should be cut IMMEDIATELY. Powell is a total disaster. We need 2% rates NOW to compete with China and Europe!",
        "source": "truth_social",
        "signal_type": "FED_PRESSURE",
        "confidence": 0.79,
        "affected_tickers": ["TLT", "GLD", "XLF", "DX-Y.NYB"],
        "affected_sectors": ["Financials", "Utilities"],
        "llm_reasoning": "Direct Fed rate pressure from executive. Historically 79% accuracy. Rate-cut expectation bullish for long duration bonds and gold, bearish for banks on NIM compression. Dollar weakness likely.",
        "offset_hours": 36,
    },
    {
        "raw_text": "MASSIVE new LNG export deal signed today. We are going to DOMINATE global energy. Europe needs our gas and we are delivering. American Energy Independence is HERE!",
        "source": "wh_press",
        "signal_type": "ENERGY_POLICY",
        "confidence": 0.76,
        "affected_tickers": ["XLE", "CL=F", "LNG", "CVX"],
        "affected_sectors": ["Energy"],
        "llm_reasoning": "Concrete LNG export expansion. Bullish for domestic energy producers and LNG infrastructure. European energy security demand real and sustained. Moderate confidence — execution timeline uncertain.",
        "offset_hours": 52,
    },
    {
        "raw_text": "New sanctions announced on Iranian oil. Zero tolerance. Any country buying Iranian oil will face SECONDARY SANCTIONS. This is effective immediately.",
        "source": "wh_press",
        "signal_type": "SANCTIONS",
        "confidence": 0.73,
        "affected_tickers": ["CL=F", "XLE", "GC=F"],
        "affected_sectors": ["Energy"],
        "llm_reasoning": "Secondary sanctions on Iranian oil historically tighten global supply. Brent crude and domestic producers benefit. Gold as geopolitical hedge. Execution risk from diplomatic complexity.",
        "offset_hours": 70,
    },
]

print(f"Seeding {len(SIGNALS)} Trump signals + predictions...")
sig_ids = []
for s in SIGNALS:
    posted = now - timedelta(hours=s["offset_hours"])
    sig = TrumpSignal(
        raw_text=s["raw_text"],
        source=s["source"],
        posted_at=posted,
        signal_type=s["signal_type"],
        confidence=s["confidence"],
        affected_tickers=s["affected_tickers"],
        affected_sectors=s["affected_sectors"],
        llm_reasoning=s["llm_reasoning"],
    )
    db.add(sig)
    db.flush()
    sig_ids.append(sig.id)

db.commit()

# ── Predictions ────────────────────────────────────────────────────────────────
PREDICTIONS = [
    {
        "sig_idx": 0,
        "buy_list": [
            {"ticker": "GLD", "reason": "Safe haven demand surge on trade war escalation"},
            {"ticker": "XAR", "reason": "Defense spending immune to tariff risk"},
            {"ticker": "TLT", "reason": "Flight to treasuries as risk-off accelerates"},
        ],
        "short_list": [
            {"ticker": "AAPL", "reason": "~$700B China revenue exposure, supply chain risk"},
            {"ticker": "NVDA", "reason": "China chip export restrictions tighten further"},
        ],
        "reasoning": "145% tariff is the largest since Smoot-Hawley. Tech supply chains critically exposed. Gold and defense as counter-cyclical longs.",
        "confidence": 0.91,
        "horizon_days": 14,
    },
    {
        "sig_idx": 2,
        "buy_list": [
            {"ticker": "TLT", "reason": "Rate cut expectations boost long-duration bonds"},
            {"ticker": "GLD", "reason": "Dollar weakness from rate pressure lifts gold"},
            {"ticker": "XLU", "reason": "Utilities rally on lower discount rate expectations"},
        ],
        "short_list": [
            {"ticker": "XLF", "reason": "NIM compression on lower rates hurts bank earnings"},
            {"ticker": "DX-Y.NYB", "reason": "Dollar weakens on rate cut expectation"},
        ],
        "reasoning": "Fed pressure narrative historically precedes actual rate cuts by 2-3 months. Rate-sensitive assets lead the move.",
        "confidence": 0.79,
        "horizon_days": 30,
    },
]

for p in PREDICTIONS:
    sig_id = sig_ids[p["sig_idx"]]
    db.add(Prediction(
        signal_id=sig_id,
        buy_list=p["buy_list"],
        short_list=p["short_list"],
        reasoning=p["reasoning"],
        confidence=p["confidence"],
        horizon_days=p["horizon_days"],
        created_at=now - timedelta(hours=SIGNALS[p["sig_idx"]]["offset_hours"] - 1),
    ))
db.commit()

# ── News Articles ──────────────────────────────────────────────────────────────
NEWS = [
    ("Trump imposes 145% tariff on Chinese electronics, market selloff accelerates", "NewsAPI", "https://reuters.com", ["tariffs", "china", "tech"], 1),
    ("Fed officials signal willingness to cut rates if economy weakens further", "NewsAPI", "https://wsj.com", ["fed", "rates"], 3),
    ("NVIDIA faces new export restrictions as US-China tensions escalate", "NewsAPI", "https://bloomberg.com", ["nvda", "china", "semis"], 2),
    ("S&P 500 erases losses after Trump-Xi call optimism boosts sentiment", "NewsAPI", "https://cnbc.com", ["spy", "china", "trade"], 5),
    ("Apple scrambles to shift production out of China amid tariff chaos", "NewsAPI", "https://ft.com", ["aapl", "tariffs", "supply-chain"], 4),
    ("White House announces sweeping deregulation for domestic energy sector", "WH Press", "https://whitehouse.gov", ["energy", "deregulation"], 6),
    ("Gold hits 18-month high as investors flee to safe havens", "NewsAPI", "https://marketwatch.com", ["gld", "gold", "safe-haven"], 2),
    ("Treasury yields fall as rate cut bets surge on Trump Fed comments", "NewsAPI", "https://reuters.com", ["tlt", "rates", "fed"], 4),
    ("Iranian sanctions push crude oil above $85, energy stocks rally", "WH Press", "https://bloomberg.com", ["cl=f", "energy", "sanctions"], 1),
    ("LNG export terminal capacity to triple under new energy executive order", "WH Press", "https://whitehouse.gov", ["energy", "lng", "exports"], 7),
    ("Bitcoin surges past $94K as crypto-friendly regulatory signals emerge", "NewsAPI", "https://coindesk.com", ["btc", "crypto"], 3),
    ("Dollar weakens against euro and yen amid Fed rate cut speculation", "NewsAPI", "https://ft.com", ["dxy", "forex", "fed"], 5),
    ("Defense sector outperforms as Pentagon budget boost confirmed", "NewsAPI", "https://defensenews.com", ["xar", "defense"], 8),
    ("China retaliates with 125% tariffs on US agricultural exports", "NewsAPI", "https://reuters.com", ["tariffs", "china", "agriculture"], 2),
    ("Tesla gains on optimism about regulatory rollback under new DOT rules", "NewsAPI", "https://electrek.co", ["tsla", "ev", "deregulation"], 6),
    ("European markets mixed as investors weigh US trade policy uncertainty", "NewsAPI", "https://reuters.com", ["^gdaxi", "^ftse", "europe"], 9),
    ("Fed chair Powell: rate decisions remain data-dependent despite political pressure", "NewsAPI", "https://wsj.com", ["fed", "rates", "powell"], 4),
    ("Goldman Sachs raises S&P 500 year-end target to 5,800 on AI tailwinds", "NewsAPI", "https://bloomberg.com", ["spy", "ai", "equities"], 10),
    ("Nikkei hits record as yen weakness boosts Japanese export earnings", "NewsAPI", "https://reuters.com", ["^n225", "japan", "yen"], 8),
    ("US sanctions trigger 3% oil spike; XLE ETF sees record inflows", "NewsAPI", "https://marketwatch.com", ["xle", "cl=f", "energy"], 3),
]

print(f"Seeding {len(NEWS)} news articles...")
for headline, source, url, tags, offset_hours in NEWS:
    db.add(NewsArticle(
        headline=headline,
        source=source,
        url=url,
        published_at=now - timedelta(hours=offset_hours),
        tags=tags,
    ))
db.commit()

db.close()
print("✓ Seed complete. Refresh http://localhost:3002")
