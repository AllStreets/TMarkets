import logging
import requests
from datetime import datetime
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import NewsArticle
from app.config import settings

logger = logging.getLogger(__name__)

def fetch_newsapi(api_key: str, query: str = "markets finance Trump") -> list:
    resp = requests.get(
        "https://newsapi.org/v2/everything",
        params={"q": query, "language": "en", "sortBy": "publishedAt", "pageSize": 20, "apiKey": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    return [
        {
            "headline": a["title"],
            "url": a["url"],
            "source": a.get("source", {}).get("name", "NewsAPI"),
            "published_at": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None),
            "tags": ["markets"],
        }
        for a in articles if a.get("title")
    ]

def fetch_gnews(api_key: str) -> list:
    resp = requests.get(
        "https://gnews.io/api/v4/search",
        params={"q": "Trump markets finance", "lang": "en", "max": 10, "token": api_key},
        timeout=10,
    )
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    return [
        {
            "headline": a["title"],
            "url": a["url"],
            "source": a.get("source", {}).get("name", "GNews"),
            "published_at": datetime.fromisoformat(a["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None),
            "tags": ["markets"],
        }
        for a in articles if a.get("title")
    ]

def store_articles(articles: list, db) -> None:
    existing_urls = {r.url for r in db.query(NewsArticle.url).all()}
    for a in articles:
        if a["url"] not in existing_urls:
            db.add(NewsArticle(**a))
    db.commit()

@celery.task(name="app.workers.news_feed.fetch_news_task")
def fetch_news_task():
    db = SessionLocal()
    try:
        articles = []
        if settings.news_api_key:
            try:
                articles += fetch_newsapi(settings.news_api_key)
            except Exception as e:
                logger.warning("NewsAPI fetch failed: %r", e)
        if settings.gnews_api_key:
            try:
                articles += fetch_gnews(settings.gnews_api_key)
            except Exception as e:
                logger.warning("GNews fetch failed: %r", e)
        store_articles(articles, db)
    finally:
        db.close()
