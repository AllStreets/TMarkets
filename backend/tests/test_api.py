import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_market_quotes_returns_list():
    mock_rows = [MagicMock(symbol="SPY", price=541.2, change_pct=1.24, volume=80e6, source="yfinance", fetched_at=MagicMock(isoformat=lambda: "2026-04-25T10:00:00"))]
    with patch("app.routers.market.get_latest_quotes", return_value=mock_rows):
        resp = client.get("/api/market/quotes")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "SPY"

def test_signals_latest_returns_signal():
    mock_sig = MagicMock(
        id=1, raw_text="Tariffs on China 145%", source="truth_social",
        signal_type="TRADE_TARIFF", confidence=0.87,
        affected_tickers=["AAPL"], affected_sectors=["Technology"],
        posted_at=MagicMock(isoformat=lambda: "2026-04-25T09:42:00"),
        llm_reasoning="test",
    )
    with patch("app.routers.signals.get_latest_signal", return_value=mock_sig):
        resp = client.get("/api/signals/latest")
    assert resp.status_code == 200
    assert resp.json()["signal_type"] == "TRADE_TARIFF"
