from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NewsArticle
from app.schemas import NewsSchema

router = APIRouter(prefix="/api/news")


@router.get("/feed", response_model=list)
def news_feed(limit: int = 30, db: Session = Depends(get_db)):
    articles = db.query(NewsArticle).order_by(NewsArticle.published_at.desc()).limit(limit).all()
    return [
        NewsSchema(
            id=a.id,
            headline=a.headline,
            source=a.source,
            url=a.url,
            published_at=a.published_at.isoformat(),
            tags=a.tags,
        ).dict()
        for a in articles
    ]
