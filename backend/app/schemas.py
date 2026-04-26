from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel


class QuoteSchema(BaseModel):
    symbol: str
    price: float
    change_pct: float
    volume: Optional[float]
    source: str
    fetched_at: str


class SignalSchema(BaseModel):
    id: int
    raw_text: str
    source: str
    signal_type: Optional[str]
    confidence: Optional[float]
    affected_tickers: Optional[List[str]]
    affected_sectors: Optional[List[str]]
    llm_reasoning: Optional[str]
    posted_at: str


class PredictionSchema(BaseModel):
    id: int
    signal_id: int
    buy_list: List[Any]
    short_list: List[Any]
    reasoning: str
    confidence: float
    horizon_days: int
    created_at: str


class NewsSchema(BaseModel):
    id: int
    headline: str
    source: str
    url: str
    published_at: str
    tags: Optional[List[str]]
