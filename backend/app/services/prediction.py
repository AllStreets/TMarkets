from __future__ import annotations

import json
import logging
from datetime import datetime

from openai import OpenAI
from app.workers.celery_app import celery
from app.database import SessionLocal
from app.models import TrumpSignal, Prediction, MarketData
from app.config import settings

logger = logging.getLogger(__name__)

CLASSIFY_SYSTEM_PROMPT = """You are a financial signal classifier. Given a statement by Trump or the White House, return a JSON object with exactly these fields:
- signal_type: one of TRADE_TARIFF, FED_PRESSURE, ENERGY_POLICY, INTL_POLICY, FISCAL_POLICY, SANCTIONS, DEREGULATION, OTHER
- affected_tickers: list of up to 6 most-impacted US stock/ETF tickers
- affected_sectors: list of sector names
- directional_bias: dict mapping ticker to "positive" or "negative"
- reasoning: one sentence explanation
- llm_confidence: float 0.0-1.0

Return only valid JSON, no markdown."""

SIGNAL_TYPE_ACCURACY = {
    "TRADE_TARIFF": 0.84, "FED_PRESSURE": 0.79, "ENERGY_POLICY": 0.76,
    "INTL_POLICY": 0.68, "FISCAL_POLICY": 0.61, "OTHER": 0.55,
}

SAFETY_BUYS = {
    "TRADE_TARIFF": ["GLD", "TLT", "SH"],
    "FED_PRESSURE": ["GLD", "TLT"],
    "ENERGY_POLICY": ["XLE"],
}
SAFETY_SHORTS = {
    "TRADE_TARIFF": ["FXI", "KWEB"],
    "FED_PRESSURE": ["KRE"],
}


def classify_signal(text: str, client: OpenAI) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": CLASSIFY_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        max_tokens=400,
    )
    return json.loads(resp.choices[0].message.content)


def compute_confidence(llm_confidence: float, similar_signals_found: int, historical_accuracy: float) -> float:
    quant_coverage = min(similar_signals_found, 20) / 20
    return (llm_confidence * 0.5) + (quant_coverage * 0.3) + (historical_accuracy * 0.2)


def find_similar_signals(signal_type: str, db) -> int:
    return db.query(TrumpSignal).filter(TrumpSignal.signal_type == signal_type).count()


def build_recommendation(classification: dict, confidence: float) -> dict:
    signal_type = classification.get("signal_type", "OTHER")
    bias = classification.get("directional_bias", {})
    buy_list = [
        {"ticker": t, "reason": f"Directional bias: positive per {signal_type}"}
        for t, direction in bias.items() if direction == "positive"
    ] + [
        {"ticker": t, "reason": f"Historical safety play for {signal_type}"}
        for t in SAFETY_BUYS.get(signal_type, []) if t not in bias
    ]
    short_list = [
        {"ticker": t, "reason": classification.get("reasoning", "")}
        for t, direction in bias.items() if direction == "negative"
    ] + [
        {"ticker": t, "reason": f"Historical short for {signal_type}"}
        for t in SAFETY_SHORTS.get(signal_type, []) if t not in bias
    ]
    return {
        "buy_list": buy_list[:4],
        "short_list": short_list[:4],
        "reasoning": classification.get("reasoning", ""),
        "confidence": confidence,
        "horizon_days": 5,
    }


@celery.task(name="app.services.prediction.run_prediction_pipeline")
def run_prediction_pipeline(signal_id: int):
    db = SessionLocal()
    try:
        sig = db.query(TrumpSignal).filter_by(id=signal_id).first()
        if not sig:
            return
        client = OpenAI(api_key=settings.openai_api_key)
        classification = classify_signal(sig.raw_text, client)
        signal_type = classification.get("signal_type", "OTHER")
        similar_count = find_similar_signals(signal_type, db)
        hist_accuracy = SIGNAL_TYPE_ACCURACY.get(signal_type, 0.55)
        confidence = compute_confidence(
            llm_confidence=classification.get("llm_confidence", 0.5),
            similar_signals_found=similar_count,
            historical_accuracy=hist_accuracy,
        )
        sig.signal_type = signal_type
        sig.affected_tickers = classification.get("affected_tickers", [])
        sig.affected_sectors = classification.get("affected_sectors", [])
        sig.directional_bias = classification.get("directional_bias", {})
        sig.confidence = confidence
        sig.llm_reasoning = classification.get("reasoning", "")
        db.commit()
        if confidence < 0.55:
            return
        rec = build_recommendation(classification, confidence)
        pred = Prediction(signal_id=signal_id, **rec)
        db.add(pred)
        db.commit()
        db.refresh(pred)
        from app.services.notifications import broadcast_prediction
        broadcast_prediction.delay(pred.id)
    except Exception as e:
        db.rollback()
        logger.error("Prediction pipeline failed for signal %d: %r", signal_id, e)
        raise
    finally:
        db.close()
