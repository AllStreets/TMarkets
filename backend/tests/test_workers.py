from unittest.mock import patch, MagicMock
from app.workers.market_data import fetch_quotes

SYMBOLS = ["SPY", "QQQ", "GLD"]

def test_fetch_quotes_stores_records(db):
    mock_ticker = MagicMock()
    mock_ticker.fast_info.last_price = 541.2
    mock_ticker.fast_info.previous_close = 534.5

    with patch("app.workers.market_data.yf.Ticker", return_value=mock_ticker):
        fetch_quotes(SYMBOLS, db)

    from app.models import MarketData
    rows = db.query(MarketData).all()
    assert len(rows) == 3
    assert rows[0].symbol == "SPY"
    assert abs(rows[0].change_pct - ((541.2 - 534.5) / 534.5 * 100)) < 0.01
    assert rows[0].source == "yfinance"
