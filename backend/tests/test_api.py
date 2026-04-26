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


from app.services.notifications import format_alert_payload
from app.services.email_service import build_brief_html

def test_format_alert_payload_structure():
    from app.models import Prediction, TrumpSignal
    pred = Prediction(
        id=1, signal_id=1,
        buy_list=[{"ticker": "GLD", "reason": "safety"}],
        short_list=[{"ticker": "AAPL", "reason": "exposure"}],
        reasoning="Tariff escalation", confidence=0.87, horizon_days=5,
    )
    sig = TrumpSignal(id=1, raw_text="Tariffs 145%", source="truth_social", signal_type="TRADE_TARIFF")
    payload = format_alert_payload(pred, sig)
    assert payload["type"] == "alert"
    assert payload["confidence"] == 0.87
    assert any(b["ticker"] == "GLD" for b in payload["buy_list"])

def test_build_brief_html_contains_sections():
    html = build_brief_html(signals=[], top_movers=[], macro_notes=[], earnings=[])
    assert "<html" in html
    assert "TMarkets" in html
    assert "7am Brief" in html
