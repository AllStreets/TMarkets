from datetime import datetime
from app.models import MarketData, TrumpSignal, Prediction, NewsArticle, MacroData

def test_market_data_insert(db):
    row = MarketData(symbol="SPY", price=541.2, change_pct=1.24, volume=80e6, source="yfinance")
    db.add(row)
    db.commit()
    result = db.query(MarketData).filter_by(symbol="SPY").first()
    assert result.price == 541.2
    assert result.source == "yfinance"

def test_trump_signal_insert(db):
    sig = TrumpSignal(
        raw_text="Tariffs on China to 145%",
        source="truth_social",
        posted_at=datetime.utcnow(),
        signal_type="TRADE_TARIFF",
        affected_tickers=["AAPL", "AMZN"],
        affected_sectors=["Technology"],
        confidence=0.87,
    )
    db.add(sig)
    db.commit()
    result = db.query(TrumpSignal).first()
    assert result.signal_type == "TRADE_TARIFF"
    assert "AAPL" in result.affected_tickers

def test_prediction_insert(db):
    pred = Prediction(
        signal_id=1,
        buy_list=[{"ticker": "GLD", "reason": "flight to safety"}],
        short_list=[{"ticker": "AAPL", "reason": "China exposure"}],
        reasoning="Tariff escalation historically negative for tech",
        confidence=0.87,
        horizon_days=5,
    )
    db.add(pred)
    db.commit()
    assert db.query(Prediction).count() == 1
