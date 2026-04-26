from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery("tmarkets", broker=settings.redis_url, backend=settings.redis_url)

celery.conf.beat_schedule = {
    "fetch-quotes-every-5min": {
        "task": "app.workers.market_data.fetch_quotes_task",
        "schedule": 300,
    },
    "fetch-trump-signals-every-5min": {
        "task": "app.workers.trump_signals.fetch_trump_signals_task",
        "schedule": 300,
    },
    "fetch-macro-daily": {
        "task": "app.workers.macro_data.fetch_macro_task",
        "schedule": crontab(hour=6, minute=30),
    },
    "fetch-news-every-10min": {
        "task": "app.workers.news_feed.fetch_news_task",
        "schedule": 600,
    },
    "fetch-options-every-15min": {
        "task": "app.workers.options_flow.fetch_options_task",
        "schedule": 900,
    },
    "daily-brief": {
        "task": "app.workers.daily_brief.send_daily_brief_task",
        "schedule": crontab(hour=12, minute=0),
    },
}

celery.conf.timezone = "America/New_York"
celery.conf.enable_utc = True
celery.autodiscover_tasks(["app.workers"])
