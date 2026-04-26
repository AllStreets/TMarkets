from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction
from app.schemas import PredictionSchema

router = APIRouter(prefix="/api/predictions")


@router.get("/latest")
def latest_prediction(db: Session = Depends(get_db)):
    pred = db.query(Prediction).order_by(Prediction.created_at.desc()).first()
    if not pred:
        return {}
    return PredictionSchema(
        id=pred.id,
        signal_id=pred.signal_id,
        buy_list=pred.buy_list,
        short_list=pred.short_list,
        reasoning=pred.reasoning,
        confidence=pred.confidence,
        horizon_days=pred.horizon_days,
        created_at=pred.created_at.isoformat(),
    ).dict()
