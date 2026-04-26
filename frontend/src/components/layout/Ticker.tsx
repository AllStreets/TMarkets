'use client';
import type { Quote } from '@/lib/types';

interface TickerProps {
  quotes: Quote[];
  alerts: { signal_text: string; buy_list: { ticker: string }[]; confidence: number }[];
}

export function Ticker({ quotes, alerts }: TickerProps) {
  return (
    <div style={{
      background: 'var(--bg2)', borderBottom: '1px solid var(--border2)',
      height: 26, overflow: 'hidden', display: 'flex', alignItems: 'center',
      position: 'sticky', top: 36, zIndex: 99,
    }}>
      <div style={{ background: 'var(--cyan)', color: '#000', fontSize: 9, fontWeight: 700, letterSpacing: 1.5, padding: '0 10px', height: '100%', display: 'flex', alignItems: 'center', flexShrink: 0, fontFamily: 'Inter,sans-serif' }}>
        LIVE
      </div>
      <div style={{ overflow: 'hidden', flex: 1 }}>
        <div style={{ display: 'flex', animation: 'scroll 60s linear infinite', whiteSpace: 'nowrap', paddingLeft: 20 }}>
          {[...quotes, ...quotes].map((q, i) => (
            <span key={i} style={{ display: 'inline-flex', alignItems: 'center', gap: 5, fontSize: 10, padding: '0 18px', borderRight: '1px solid var(--border2)', height: 26 }}>
              <span style={{ color: 'var(--text2)', fontWeight: 600 }}>{q.symbol}</span>
              <span>{q.price.toFixed(2)}</span>
              <span style={{ color: q.change_pct >= 0 ? 'var(--green)' : 'var(--red)' }}>
                {q.change_pct >= 0 ? '▲' : '▼'}{Math.abs(q.change_pct).toFixed(2)}%
              </span>
            </span>
          ))}
          {alerts.map((a, i) => (
            <span key={`alert-${i}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 9, padding: '0 14px', height: 26, background: '#1a0a00', borderLeft: '2px solid #ff6b00', borderRight: '2px solid #ff6b00', color: '#ff9940' }}>
              <span style={{ background: '#ff6b00', color: '#000', fontSize: 8, fontWeight: 700, padding: '1px 5px', borderRadius: 2, letterSpacing: 1 }}>⚡ TRUMP</span>
              {a.signal_text}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
