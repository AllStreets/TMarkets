from __future__ import annotations

import logging
from datetime import datetime
from sqlalchemy import func
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import TrumpSignal, MarketData
from app.services.email_service import build_brief_html, send_brief_email

logger = logging.getLogger(__name__)


@celery.task(name="app.workers.daily_brief.send_daily_brief_task")
def send_daily_brief_task():
    db = SessionLocal()
    try:
        midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        signals = db.query(TrumpSignal).filter(TrumpSignal.posted_at >= midnight).all()
        signal_dicts = [
            {"signal_type": s.signal_type, "raw_text": s.raw_text, "confidence": s.confidence or 0}
            for s in signals
        ]
        subq = (
            db.query(MarketData.symbol, func.max(MarketData.fetched_at).label("mt"))
            .group_by(MarketData.symbol)
            .subquery()
        )
        rows = (
            db.query(MarketData)
            .join(subq, (MarketData.symbol == subq.c.symbol) & (MarketData.fetched_at == subq.c.mt))
            .all()
        )
        movers = sorted(
            [{"symbol": r.symbol, "change_pct": r.change_pct, "source": r.source} for r in rows],
            key=lambda x: abs(x["change_pct"] or 0),
            reverse=True,
        )[:10]
        html = build_brief_html(signals=signal_dicts, top_movers=movers, macro_notes=[], earnings=[])
        send_brief_email(html)
    except Exception as e:
        logger.error("Daily brief task failed: %r", e)
        raise
    finally:
        db.close()
