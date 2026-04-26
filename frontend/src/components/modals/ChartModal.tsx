'use client';
import { useEffect } from 'react';
import { Sparkline } from '@/components/shared/Sparkline';

interface ChartModalProps {
  open: boolean;
  symbol: string;
  price: string;
  change: string;
  direction: 'bull' | 'bear' | 'neutral';
  source: string;
  data: number[];
  onClose: () => void;
}

export function ChartModal({ open, symbol, price, change, direction, source, data, onClose }: ChartModalProps) {
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  if (!open) return null;
  const color = direction === 'bull' ? 'var(--green)' : direction === 'bear' ? 'var(--red)' : 'var(--blue)';

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      style={{ position: 'fixed', inset: 0, background: '#00000099', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}
    >
      <div style={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, padding: 20, width: 700, maxWidth: '95vw', position: 'relative' }}>
        <div onClick={onClose} style={{ position: 'absolute', top: 12, right: 14, color: 'var(--text3)', cursor: 'pointer', fontSize: 16 }}>✕</div>
        <div style={{ color: 'var(--cyan)', fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{symbol}</div>
        <div style={{ fontSize: 10, color: 'var(--text3)', fontFamily: 'Inter,sans-serif', marginBottom: 16 }}>
          {price} · {change} · 30-day · {source}
        </div>
        {data.length > 1
          ? <Sparkline data={data} color={color} height={180} />
          : <div style={{ height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text3)', fontSize: 12 }}>No history available</div>
        }
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8, marginTop: 16 }}>
          {['Open', 'High', 'Low', 'Volume'].map(k => (
            <div key={k} className="tile">
              <div className="tile-label">{k}</div>
              <div className="tile-val" style={{ fontSize: 13 }}>—</div>
            </div>
          ))}
        </div>
        <div className="cite" style={{ marginTop: 10 }}>Data: {source} · Delayed 15 min on free tier</div>
      </div>
    </div>
  );
}
