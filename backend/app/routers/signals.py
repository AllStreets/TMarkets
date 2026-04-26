from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TrumpSignal
from app.schemas import SignalSchema

router = APIRouter(prefix="/api/signals")


def get_latest_signal(db: Session):
    return db.query(TrumpSignal).order_by(TrumpSignal.posted_at.desc()).first()


def _to_schema(sig) -> dict:
    return SignalSchema(
        id=sig.id,
        raw_text=sig.raw_text,
        source=sig.source,
        signal_type=sig.signal_type,
        confidence=sig.confidence,
        affected_tickers=sig.affected_tickers,
        affected_sectors=sig.affected_sectors,
        llm_reasoning=sig.llm_reasoning,
        posted_at=sig.posted_at.isoformat(),
    ).dict()


@router.get("/latest")
def latest_signal(db: Session = Depends(get_db)):
    sig = get_latest_signal(db)
    if not sig:
        return {}
    return _to_schema(sig)


@router.get("/history", response_model=list)
def signal_history(limit: int = 10, db: Session = Depends(get_db)):
    sigs = db.query(TrumpSignal).order_by(TrumpSignal.posted_at.desc()).limit(limit).all()
    return [_to_schema(s) for s in sigs]
