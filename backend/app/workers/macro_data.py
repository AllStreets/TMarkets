import logging
from datetime import datetime
from fredapi import Fred
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import MacroData
from app.config import settings

logger = logging.getLogger(__name__)

FRED_SERIES = [
    ("FEDFUNDS", "Fed Funds Rate"),
    ("CPIAUCSL", "CPI YoY"),
    ("GS10", "10Y Treasury"),
    ("UNRATE", "Unemployment"),
    ("A191RL1Q225SBEA", "GDP Growth"),
    ("M2SL", "M2 Money Supply"),
]

def fetch_fred_series(series_id: str, label: str, db) -> None:
    fred = Fred(api_key=settings.fred_api_key)
    data = fred.get_series(series_id)
    if data.empty:
        return
    value = float(data.iloc[-1])
    period = str(data.index[-1].date())
    row = MacroData(indicator=series_id, value=value, period=period, source="FRED", fetched_at=datetime.utcnow())
    db.add(row)
    db.commit()

@celery.task(name="app.workers.macro_data.fetch_macro_task")
def fetch_macro_task():
    db = SessionLocal()
    try:
        for series_id, label in FRED_SERIES:
            try:
                fetch_fred_series(series_id, label, db)
            except Exception as e:
                db.rollback()
                logger.warning("Failed to fetch FRED series %s: %r", series_id, e)
    finally:
        db.close()
