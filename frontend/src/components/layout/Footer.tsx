export function Footer() {
  const nextBrief = () => {
    const now = new Date();
    const est = new Date(now.toLocaleString('en-US', { timeZone: 'America/New_York' }));
    const next = new Date(est);
    next.setHours(7, 0, 0, 0);
    if (est >= next) next.setDate(next.getDate() + 1);
    const diff = next.getTime() - est.getTime();
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    return `${h}h ${m}m`;
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', borderTop: '1px solid var(--border2)', background: 'var(--bg)', fontSize: 8.5, color: 'var(--text4)', fontFamily: 'Inter,sans-serif' }}>
      <div>TMarkets · All data cited per tile · Not financial advice</div>
      <div style={{ display: 'flex', gap: 16 }}>
        <span>Sources: yfinance · Alpha Vantage · FRED · NewsAPI · GNews · Truth Social · WH Press · Polygon.io · SEC EDGAR</span>
        <span>Algorithm: GPT-4.1-mini + Quant</span>
        <span>Next 7am brief: {nextBrief()}</span>
      </div>
    </div>
  );
}
