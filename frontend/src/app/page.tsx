'use client';
import { useState, useCallback } from 'react';
import { Topbar } from '@/components/layout/Topbar';
import { Ticker } from '@/components/layout/Ticker';
import { Footer } from '@/components/layout/Footer';
import { IndexTile } from '@/components/tiles/IndexTile';
import { MacroTile } from '@/components/tiles/MacroTile';
import { ChartTile } from '@/components/tiles/ChartTile';
import { HeatmapTile } from '@/components/tiles/HeatmapTile';
import { NewsTile } from '@/components/tiles/NewsTile';
import { TrumpSignalPanel } from '@/components/panels/TrumpSignalPanel';
import { AIRecommendationPanel } from '@/components/panels/AIRecommendationPanel';
import { SignalHistoryPanel } from '@/components/panels/SignalHistoryPanel';
import { ChartModal } from '@/components/modals/ChartModal';
import { SignalDetailModal } from '@/components/modals/SignalDetailModal';
import { AlertBanner } from '@/components/shared/AlertBanner';
import { useMarketData } from '@/hooks/useMarketData';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { AlertPayload, Quote, TrumpSignal } from '@/lib/types';

const INDEX_SYMS = ['SPY','QQQ','DIA','VIX','IWM','DXY'];
const MACRO_TILES = [
  { label: 'Fed Funds Rate', indicator: 'FEDFUNDS', color: 'var(--blue)', source: 'FRED' },
  { label: 'CPI YoY', indicator: 'CPIAUCSL', color: 'var(--amber)', source: 'BLS via FRED' },
  { label: '10Y Treasury', indicator: 'GS10', color: 'var(--text)', source: 'US Treasury · FRED' },
  { label: 'Unemployment', indicator: 'UNRATE', color: 'var(--text)', source: 'BLS via FRED' },
  { label: 'GDP Growth', indicator: 'A191RL1Q225SBEA', color: 'var(--green)', source: 'BEA via FRED' },
  { label: 'M2 Money Supply', indicator: 'M2SL', color: 'var(--text)', source: 'Fed · FRED' },
];
const WATCHLIST_ROW1 = ['AAPL','NVDA','TSLA','GLD','TLT'];
const WATCHLIST_ROW2 = ['MSFT','META','AMZN','XAR','BTC-USD'];
const INTL = ['^HSI','000001.SS','^N225','^GDAXI','^FTSE','^FCHI','BVSP','GSPTSE'];

function fakeHistory(_sym: string, up: boolean) {
  return Array.from({ length: 30 }, (_, i) => 100 + (up ? 1 : -1) * i * 0.4 + Math.sin(i) * 2);
}

export default function Dashboard() {
  const { quotes, signal, signalHistory, prediction, news, refresh } = useMarketData();
  const [alerts, setAlerts] = useState<AlertPayload[]>([]);
  const [chartModal, setChartModal] = useState<{ open: boolean; quote: Quote | null }>({ open: false, quote: null });
  const [signalModal, setSignalModal] = useState<{ open: boolean; signal: TrumpSignal | null }>({ open: false, signal: null });

  const handleMessage = useCallback((data: unknown) => {
    const payload = data as AlertPayload;
    if (payload.type === 'alert') {
      setAlerts(prev => [payload, ...prev].slice(0, 5));
      new Audio('/chime.mp3').play().catch(() => {});
      refresh();
    }
  }, [refresh]);

  useWebSocket(handleMessage);

  const quoteMap = Object.fromEntries(quotes.map(q => [q.symbol, q]));

  const openChart = (q: Quote) => setChartModal({ open: true, quote: q });
  const openSignal = (s: TrumpSignal) => setSignalModal({ open: true, signal: s });

  const newsBreaking = news.filter((_, i) => i % 3 === 0).slice(0, 4);
  const newsPolicy = news.filter((_, i) => i % 3 === 1).slice(0, 4);
  const newsMovers = news.filter((_, i) => i % 3 === 2).slice(0, 4);

  return (
    <>
      <Topbar alertCount={alerts.length} />
      <Ticker quotes={quotes} alerts={alerts} />

      <div className="dash">
        <div className="section-header">Major Indices</div>
        <div className="g6">
          {INDEX_SYMS.filter(sym => quoteMap[sym]).map(sym => <IndexTile key={sym} quote={quoteMap[sym]} onClick={openChart} />)}
        </div>

        <div className="section-header">Macro Indicators · FRED</div>
        <div className="g6">
          {MACRO_TILES.map(m => (
            <MacroTile key={m.indicator} label={m.label} value="—" sub="Loading…" color={m.color} source={m.source} onClick={() => {}} />
          ))}
        </div>

        <div className="section-header">Commodities &amp; Currencies</div>
        <div className="g6">
          {['GC=F','CL=F','SI=F','EURUSD=X','CNY=X','JPY=X'].filter(sym => quoteMap[sym]).map(sym => <IndexTile key={sym} quote={quoteMap[sym]} onClick={openChart} />)}
        </div>

        <div className="section-header">Trump Signal · AI Recommendation · Sectors</div>
        <div className="g-trump">
          <TrumpSignalPanel signal={signal} onClick={openSignal} />
          <AIRecommendationPanel prediction={prediction} />
          <HeatmapTile quotes={quotes} onSectorClick={etf => quoteMap[etf] && openChart(quoteMap[etf])} />
        </div>

        <div className="section-header">Mega-Cap Watchlist · Click to Expand</div>
        <div className="g5">
          {WATCHLIST_ROW1.filter(sym => quoteMap[sym]).map(sym => <ChartTile key={sym} quote={quoteMap[sym]} history={fakeHistory(sym, quoteMap[sym].change_pct >= 0)} onClick={openChart} />)}
        </div>
        <div className="g5">
          {WATCHLIST_ROW2.filter(sym => quoteMap[sym]).map(sym => <ChartTile key={sym} quote={quoteMap[sym]} history={fakeHistory(sym, quoteMap[sym].change_pct >= 0)} onClick={openChart} />)}
        </div>

        <div className="section-header">Trump Signal History · Algorithmic Impact Log</div>
        <div className="g2">
          <SignalHistoryPanel signals={signalHistory} onSelect={openSignal} />
          <div className="tile" style={{ padding: '11px 13px' }}>
            <div className="tile-label" style={{ marginBottom: 8 }}>International Markets</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 6 }}>
              {INTL.map(sym => {
                const q = quoteMap[sym];
                if (!q) return null;
                return (
                  <div key={sym} onClick={() => openChart(q)} className="tile" style={{ padding: '6px 8px' }}>
                    <div className="tile-label" style={{ fontSize: 8 }}>{sym}</div>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{q.price.toLocaleString()}</div>
                    <div className={`tile-change ${q.change_pct >= 0 ? 'up' : 'dn'}`} style={{ fontSize: 9 }}>{q.change_pct >= 0 ? '▲' : '▼'}{Math.abs(q.change_pct).toFixed(2)}%</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="section-header">News Feed · Click Any Story to Open</div>
        <div className="g3">
          <NewsTile title="Breaking · NewsAPI" articles={newsBreaking} source="NewsAPI" />
          <NewsTile title="Policy &amp; Regulation · WH Press" articles={newsPolicy} source="WH Press · NewsAPI" />
          <NewsTile title="Watchlist Movers · GNews" articles={newsMovers} source="GNews · yfinance" />
        </div>
      </div>

      <Footer />

      <ChartModal
        open={chartModal.open}
        symbol={chartModal.quote?.symbol ?? ''}
        price={chartModal.quote?.price.toFixed(2) ?? ''}
        change={chartModal.quote ? `${chartModal.quote.change_pct >= 0 ? '+' : ''}${chartModal.quote.change_pct.toFixed(2)}%` : ''}
        direction={(chartModal.quote?.change_pct ?? 0) >= 0 ? 'bull' : 'bear'}
        source={chartModal.quote?.source ?? ''}
        data={fakeHistory(chartModal.quote?.symbol ?? '', (chartModal.quote?.change_pct ?? 0) >= 0)}
        onClose={() => setChartModal({ open: false, quote: null })}
      />

      <SignalDetailModal
        open={signalModal.open}
        signal={signalModal.signal}
        prediction={prediction}
        onClose={() => setSignalModal({ open: false, signal: null })}
      />

      <AlertBanner alert={alerts[0] ?? null} />
    </>
  );
}
