from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app.models import MarketData, TrumpSignal, Prediction, NewsArticle
from datetime import datetime

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_db(db):
    """Wire the test db session into the app's dependency injection."""
    def _override():
        yield db

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


def test_health(db):
    r = client.get("/health")
    assert r.status_code == 200


def test_quotes_empty_returns_list(db):
    r = client.get("/api/market/quotes")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_signals_empty_returns_gracefully(db):
    r = client.get("/api/signals/latest")
    assert r.status_code in (200, 404)


def test_news_empty_returns_list(db):
    r = client.get("/api/news/feed")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_full_pipeline_with_seeded_data(db):
    db.add(MarketData(symbol="SPY", price=541.2, change_pct=1.24, volume=80e6, source="yfinance", fetched_at=datetime.utcnow()))
    sig = TrumpSignal(raw_text="Tariffs on China 145%", source="truth_social", posted_at=datetime.utcnow(), signal_type="TRADE_TARIFF", confidence=0.87, affected_tickers=["AAPL"], affected_sectors=["Technology"])
    db.add(sig)
    db.commit()
    db.refresh(sig)
    pred = Prediction(signal_id=sig.id, buy_list=[{"ticker": "GLD", "reason": "safety"}], short_list=[{"ticker": "AAPL", "reason": "exposure"}], reasoning="test", confidence=0.87, horizon_days=5)
    db.add(pred)
    db.commit()

    r_quotes = client.get("/api/market/quotes")
    assert any(q["symbol"] == "SPY" for q in r_quotes.json())

    r_sig = client.get("/api/signals/latest")
    assert r_sig.json()["signal_type"] == "TRADE_TARIFF"

    r_pred = client.get("/api/predictions/latest")
    assert r_pred.json()["confidence"] == 0.87
