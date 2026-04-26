from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class MarketData(Base):
    __tablename__ = "market_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    price: Mapped[float] = mapped_column(Float)
    change_pct: Mapped[float] = mapped_column(Float)
    volume: Mapped[Optional[float]] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(50))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class TrumpSignal(Base):
    __tablename__ = "trump_signals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_text: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    posted_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    signal_type: Mapped[Optional[str]] = mapped_column(String(50))
    affected_tickers: Mapped[Optional[list]] = mapped_column(JSON)
    affected_sectors: Mapped[Optional[list]] = mapped_column(JSON)
    directional_bias: Mapped[Optional[dict]] = mapped_column(JSON)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    llm_reasoning: Mapped[Optional[str]] = mapped_column(Text)

class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_id: Mapped[int] = mapped_column(Integer, index=True)
    buy_list: Mapped[list] = mapped_column(JSON)
    short_list: Mapped[list] = mapped_column(JSON)
    reasoning: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    horizon_days: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headline: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON)

class MacroData(Base):
    __tablename__ = "macro_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    indicator: Mapped[str] = mapped_column(String(50), index=True)
    value: Mapped[float] = mapped_column(Float)
    period: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50))
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
