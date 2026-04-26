from unittest.mock import patch, MagicMock
from app.workers.market_data import fetch_quotes
from app.workers.trump_signals import (
    scrape_truth_social,
    scrape_wh_press,
    fetch_trump_news,
    is_duplicate,
)

SYMBOLS = ["SPY", "QQQ", "GLD"]

def test_fetch_quotes_stores_records(db):
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 541.2
    mock_ticker.fast_info.previous_close = 534.5

    with patch("app.workers.market_data.yf.Ticker", return_value=mock_ticker):
        fetch_quotes(SYMBOLS, db)

    from app.models import MarketData
    rows = db.query(MarketData).filter(MarketData.symbol.in_(SYMBOLS)).all()
    assert len(rows) == 3
    spy_row = next(r for r in rows if r.symbol == "SPY")
    assert abs(spy_row.change_pct - ((541.2 - 534.5) / 534.5 * 100)) < 0.01
    assert spy_row.source == "yfinance"

def test_is_duplicate_detects_same_text(db):
    from app.models import TrumpSignal
    from datetime import datetime
    existing = TrumpSignal(
        raw_text="Tariffs on China raised to 145%",
        source="truth_social",
        posted_at=datetime.utcnow(),
    )
    db.add(existing)
    db.commit()
    assert is_duplicate("Tariffs on China raised to 145%!", db) is True
    assert is_duplicate("Completely different statement about energy", db) is False

def test_fetch_trump_news_filters_by_trump(db):
    fake_articles = [
        {"title": "Trump announces new tariffs on China", "url": "https://reuters.com/1",
         "publishedAt": "2026-04-25T09:42:00Z", "source": {"name": "Reuters"}},
        {"title": "Stock market rallies on tech earnings", "url": "https://bloomberg.com/2",
         "publishedAt": "2026-04-25T09:00:00Z", "source": {"name": "Bloomberg"}},
    ]
    with patch("app.workers.trump_signals.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"articles": fake_articles, "status": "ok"}
        results = fetch_trump_news("fake_key")
    assert len(results) == 1
    assert "Trump" in results[0]["text"]
