from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import settings

logger = logging.getLogger(__name__)


def build_brief_html(signals: list, top_movers: list, macro_notes: list, earnings: list) -> str:
    signal_rows = "".join(
        f"<tr><td>{s.get('signal_type', '')}</td><td>{s.get('raw_text', '')[:80]}</td>"
        f"<td>{s.get('confidence', 0):.0%}</td></tr>"
        for s in signals
    )
    mover_rows = "".join(
        f"<tr><td>{m.get('symbol', '')}</td><td>{m.get('change_pct', 0):+.2f}%</td>"
        f"<td>{m.get('source', '')}</td></tr>"
        for m in top_movers
    )
    return (
        f'<html><body style="font-family:monospace;background:#06070d;color:#c9d1e0;padding:20px">'
        f'<h1 style="color:#00d4ff">TMarkets — 7am Brief</h1>'
        f'<p style="color:#3a4a6a">Autonomous investment digest · {len(signals)} signals overnight</p>'
        f'<h2 style="color:#ff4d6d">Trump Signals</h2>'
        f'<table border="1" style="border-color:#111d35;width:100%">'
        f'<tr><th>Type</th><th>Statement</th><th>Confidence</th></tr>'
        f'{signal_rows if signal_rows else "<tr><td colspan=3>No overnight signals</td></tr>"}'
        f'</table>'
        f'<h2 style="color:#00e676">Top Movers</h2>'
        f'<table border="1" style="border-color:#111d35;width:100%">'
        f'<tr><th>Symbol</th><th>Change</th><th>Source</th></tr>'
        f'{mover_rows if mover_rows else "<tr><td colspan=3>No significant movers</td></tr>"}'
        f'</table>'
        f'<h2 style="color:#fbbf24">High-Impact Earnings Today</h2>'
        f'<p>{", ".join(earnings) if earnings else "None"}</p>'
        f'<hr style="border-color:#111d35"/>'
        f'<p style="color:#1a2a3a;font-size:11px">TMarkets · Data: yfinance, FRED, NewsAPI, Truth Social, WH Press'
        f' · Algorithm: GPT-4.1-mini + Quant · Not financial advice</p>'
        f'</body></html>'
    )


def send_brief_email(html: str) -> None:
    if not all([settings.smtp_user, settings.smtp_pass, settings.smtp_to]):
        logger.info("Email not configured, skipping brief send")
        return
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "TMarkets 7am Brief"
        msg["From"] = settings.smtp_user
        msg["To"] = settings.smtp_to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_pass)
            server.sendmail(settings.smtp_user, settings.smtp_to, msg.as_string())
    except Exception as e:
        logger.error("Failed to send daily brief email: %r", e)
