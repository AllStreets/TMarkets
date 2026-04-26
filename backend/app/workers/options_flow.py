import logging
import requests
from datetime import date
from app.workers.celery_app import celery
from app.config import settings

logger = logging.getLogger(__name__)

OPTIONS_WATCHLIST = ["AAPL", "AMZN", "GLD", "TLT", "FXI", "NVDA", "XAR"]

def fetch_polygon_options(symbol: str, api_key: str) -> list:
    resp = requests.get(
        f"https://api.polygon.io/v2/snapshot/locale/us/markets/options/tickers/O:{symbol}",
        params={"apiKey": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json().get("results", [])

@celery.task(name="app.workers.options_flow.fetch_options_task")
def fetch_options_task():
    if not settings.polygon_api_key:
        return
    for symbol in OPTIONS_WATCHLIST:
        try:
            results = fetch_polygon_options(symbol, settings.polygon_api_key)
            logger.info("Fetched %d options contracts for %s", len(results), symbol)
        except Exception as e:
            logger.warning("Options fetch failed for %s: %r", symbol, e)
