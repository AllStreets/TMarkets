from __future__ import annotations

import asyncio
import logging
import subprocess
from app.workers.celery_app import celery
from app.websocket import manager

logger = logging.getLogger(__name__)


def format_alert_payload(pred, sig) -> dict:
    return {
        "type": "alert",
        "signal_type": sig.signal_type,
        "signal_text": (sig.raw_text or "")[:120],
        "source": sig.source,
        "buy_list": pred.buy_list,
        "short_list": pred.short_list,
        "reasoning": pred.reasoning,
        "confidence": pred.confidence,
        "horizon_days": pred.horizon_days,
    }


def send_macos_notification(title: str, body: str) -> None:
    script = f'display notification "{body}" with title "{title}" sound name "Glass"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=5)
    except Exception as e:
        logger.warning("macOS notification failed: %r", e)


@celery.task(name="app.services.notifications.broadcast_prediction")
def broadcast_prediction(prediction_id: int):
    from app.database import SessionLocal
    from app.models import Prediction, TrumpSignal
    db = SessionLocal()
    try:
        pred = db.query(Prediction).filter_by(id=prediction_id).first()
        if not pred:
            return
        sig = db.query(TrumpSignal).filter_by(id=pred.signal_id).first()
        if not sig:
            return
        payload = format_alert_payload(pred, sig)
        buy_syms = ", ".join(b["ticker"] for b in (pred.buy_list or [])[:3])
        short_syms = ", ".join(s["ticker"] for s in (pred.short_list or [])[:3])
        send_macos_notification(
            title=f"TMarkets Alert — {sig.signal_type}",
            body=f"BUY {buy_syms} · SHORT {short_syms} · Conf {pred.confidence:.0%}",
        )
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(manager.broadcast(payload))
        finally:
            loop.close()
    finally:
        db.close()
