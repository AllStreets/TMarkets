import logging
import yfinance as yf
from datetime import datetime
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import MarketData

logger = logging.getLogger(__name__)

WATCHLIST = [
    "SPY", "QQQ", "DIA", "IWM", "^VIX", "DX-Y.NYB",
    "AAPL", "MSFT", "NVDA", "AMZN", "TSLA", "META", "GOOGL",
    "GLD", "TLT", "SH", "SQQQ", "XAR", "FXI", "KWEB",
    "XLE", "XLY", "XLF", "XLU", "XLB",
    "GC=F", "CL=F", "SI=F",
    "EURUSD=X", "CNY=X", "JPY=X",
    "BTC-USD", "ETH-USD",
    "^HSI", "^N225", "^GDAXI", "^FTSE",
]

def fetch_quotes(symbols: list, db) -> None:
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            last = ticker.fast_info.last_price
            prev = ticker.fast_info.previous_close
            if last is None or prev is None:
                continue
            change_pct = (last - prev) / prev * 100
            row = MarketData(
                symbol=symbol,
                price=last,
                change_pct=change_pct,
                volume=getattr(ticker.fast_info, "three_month_average_volume", None),
                source="yfinance",
                fetched_at=datetime.utcnow(),
            )
            db.add(row)
        except Exception as e:
            logger.warning("Failed to fetch %s: %r", symbol, e)
            continue

@celery.task(name="app.workers.market_data.fetch_quotes_task")
def fetch_quotes_task():
    db = SessionLocal()
    try:
        fetch_quotes(WATCHLIST, db)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
