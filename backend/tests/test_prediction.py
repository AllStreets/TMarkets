from unittest.mock import patch, MagicMock
from datetime import datetime
from app.services.prediction import classify_signal, compute_confidence, build_recommendation
from app.models import TrumpSignal

FAKE_SIGNAL = TrumpSignal(
    id=1,
    raw_text="We are raising tariffs on all Chinese goods to 145 percent.",
    source="truth_social",
    posted_at=datetime.utcnow(),
)

FAKE_GPT_RESPONSE = {
    "signal_type": "TRADE_TARIFF",
    "affected_tickers": ["AAPL", "AMZN", "FXI"],
    "affected_sectors": ["Technology", "Retail"],
    "directional_bias": {"AAPL": "negative", "GLD": "positive"},
    "reasoning": "Tariff escalation historically negative for China-exposed tech.",
    "llm_confidence": 0.87,
}

def test_classify_signal_returns_structured_output():
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"signal_type":"TRADE_TARIFF","affected_tickers":["AAPL"],"affected_sectors":["Technology"],"directional_bias":{"AAPL":"negative","GLD":"positive"},"reasoning":"test","llm_confidence":0.87}'))]
    )
    result = classify_signal(FAKE_SIGNAL.raw_text, mock_client)
    assert result["signal_type"] == "TRADE_TARIFF"
    assert result["llm_confidence"] == 0.87
    assert "AAPL" in result["affected_tickers"]

def test_compute_confidence_formula():
    conf = compute_confidence(llm_confidence=0.87, similar_signals_found=18, historical_accuracy=0.84)
    expected = 0.87 * 0.5 + (18 / 20) * 0.3 + 0.84 * 0.2
    assert abs(conf - expected) < 0.001

def test_build_recommendation_formats_calls():
    rec = build_recommendation(FAKE_GPT_RESPONSE, confidence=0.87)
    assert any(r["ticker"] == "GLD" for r in rec["buy_list"])
    assert any(r["ticker"] == "AAPL" for r in rec["short_list"])
    assert rec["horizon_days"] == 5
