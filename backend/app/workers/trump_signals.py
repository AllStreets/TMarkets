from __future__ import annotations

import logging
import requests
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import TrumpSignal
from app.config import settings
from app.services.prediction import run_prediction_pipeline

logger = logging.getLogger(__name__)

TRUMP_TERMS = ["trump", "president trump", "potus", "donald trump"]

def is_duplicate(text: str, recent_signals: list) -> bool:
    for sig in recent_signals:
        ratio = SequenceMatcher(None, text.lower(), sig.raw_text.lower()).ratio()
        if ratio > 0.85:
            return True
    return False

def fetch_trump_news(api_key: str) -> list[dict]:
    url = "https://newsapi.org/v2/everything"
    params = {"q": "Trump", "language": "en", "sortBy": "publishedAt", "pageSize": 20, "apiKey": api_key}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    results = []
    for a in articles:
        title = a.get("title", "")
        if any(t in title.lower() for t in TRUMP_TERMS):
            results.append({
                "text": title,
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", "NewsAPI"),
                "posted_at": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None),
            })
    return results

def scrape_wh_press() -> list[dict]:
    try:
        resp = requests.get("https://www.whitehouse.gov/news/", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for article in soup.select("article")[:5]:
            title_el = article.find(["h2", "h3"])
            link_el = article.find("a", href=True)
            if title_el and link_el:
                text = title_el.get_text(strip=True)
                if any(t in text.lower() for t in TRUMP_TERMS + ["executive order", "tariff", "administration"]):
                    items.append({
                        "text": text,
                        "url": link_el["href"],
                        "source": "WH Press",
                        "posted_at": datetime.utcnow(),
                    })
        return items
    except Exception as e:
        logger.warning("WH Press scrape failed: %r", e)
        return []

def scrape_truth_social() -> list[dict]:
    try:
        resp = requests.get("https://truthsocial.com/@realDonaldTrump.rss", timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        items = []
        for item in soup.find_all("item")[:10]:
            text = BeautifulSoup(item.find("description").text, "html.parser").get_text(strip=True)
            pub_date = item.find("pubDate")
            posted_at = datetime.utcnow()
            if pub_date:
                try:
                    posted_at = parsedate_to_datetime(pub_date.text).replace(tzinfo=None)
                except Exception:
                    pass
            items.append({"text": text, "source": "Truth Social", "url": "", "posted_at": posted_at})
        return items
    except Exception as e:
        logger.warning("Truth Social scrape failed: %r", e)
        return []

def ingest_signals(raw_items: list[dict], db) -> list[TrumpSignal]:
    cutoff = datetime.utcnow() - timedelta(hours=24)
    recent = db.query(TrumpSignal).filter(TrumpSignal.posted_at >= cutoff).all()
    saved = []
    for item in raw_items:
        if is_duplicate(item["text"], recent):
            continue
        sig = TrumpSignal(
            raw_text=item["text"],
            source=item["source"],
            posted_at=item["posted_at"],
        )
        db.add(sig)
        saved.append(sig)
    if saved:
        db.commit()
        for sig in saved:
            db.refresh(sig)
    return saved

@celery.task(name="app.workers.trump_signals.fetch_trump_signals_task")
def fetch_trump_signals_task():
    db = SessionLocal()
    try:
        raw = scrape_truth_social() + scrape_wh_press()
        if settings.news_api_key:
            raw += fetch_trump_news(settings.news_api_key)
        new_signals = ingest_signals(raw, db)
        for sig in new_signals:
            run_prediction_pipeline.delay(sig.id)
    except Exception:
        raise
    finally:
        db.close()
