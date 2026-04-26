from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import MarketData
from app.schemas import QuoteSchema

router = APIRouter(prefix="/api/market")


def get_latest_quotes(db: Session):
    subq = (
        db.query(MarketData.symbol, func.max(MarketData.fetched_at).label("max_ts"))
        .group_by(MarketData.symbol)
        .subquery()
    )
    return (
        db.query(MarketData)
        .join(subq, (MarketData.symbol == subq.c.symbol) & (MarketData.fetched_at == subq.c.max_ts))
        .all()
    )


@router.get("/quotes", response_model=list)
def quotes(db: Session = Depends(get_db)):
    rows = get_latest_quotes(db)
    return [
        QuoteSchema(
            symbol=r.symbol,
            price=r.price,
            change_pct=r.change_pct,
            volume=r.volume,
            source=r.source,
            fetched_at=r.fetched_at.isoformat(),
        ).dict()
        for r in rows
    ]
