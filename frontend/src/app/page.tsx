'use client';
import { useState, useCallback } from 'react';
import { Topbar } from '@/components/layout/Topbar';
import { Ticker } from '@/components/layout/Ticker';
import { Footer } from '@/components/layout/Footer';
import { useMarketData } from '@/hooks/useMarketData';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { AlertPayload } from '@/lib/types';

export default function Dashboard() {
  const { quotes, signal, signalHistory, prediction, news, refresh } = useMarketData();
  const [alerts, setAlerts] = useState<AlertPayload[]>([]);

  const handleMessage = useCallback((data: unknown) => {
    const payload = data as AlertPayload;
    if (payload.type === 'alert') {
      setAlerts(prev => [payload, ...prev].slice(0, 5));
      const audio = new Audio('/chime.mp3');
      audio.play().catch(() => {});
      refresh();
    }
  }, [refresh]);

  useWebSocket(handleMessage);

  return (
    <>
      <Topbar alertCount={alerts.length} />
      <Ticker quotes={quotes} alerts={alerts} />
      <div className="dash">
        <div className="section-header">Loading tiles…</div>
        <pre style={{ color: 'var(--text3)', fontSize: 10 }}>
          Quotes: {quotes.length} · Signal: {signal?.signal_type ?? 'none'} · News: {news.length}
        </pre>
      </div>
      <Footer />
    </>
  );
}
