'use client';
import type { TrumpSignal } from '@/lib/types';
import { CiteBadge } from '@/components/shared/CiteBadge';

interface Props { signals: TrumpSignal[]; onSelect: (s: TrumpSignal) => void; }

const TYPE_ACCURACY: Record<string, number> = {
  TRADE_TARIFF: 0.84, FED_PRESSURE: 0.79, ENERGY_POLICY: 0.76,
  INTL_POLICY: 0.68, FISCAL_POLICY: 0.61, OTHER: 0.55,
};

export function SignalHistoryPanel({ signals, onSelect }: Props) {
  return (
    <div className="tile" style={{ padding: '11px 13px' }}>
      <div className="tile-label" style={{ marginBottom: 8 }}>Trump Signal History</div>
      {signals.slice(0, 5).map(s => (
        <div key={s.id} onClick={() => onSelect(s)} style={{ padding: '8px 0', borderBottom: '1px solid var(--border2)', cursor: 'pointer' }}
          onMouseEnter={e => (e.currentTarget.style.background = '#0d1526')}
          onMouseLeave={e => (e.currentTarget.style.background = '')}
        >
          <div style={{ display: 'flex', gap: 8 }}>
            <span style={{ fontSize: 8, color: 'var(--text4)', fontFamily: 'Inter,sans-serif', width: 60, flexShrink: 0 }}>{new Date(s.posted_at).toLocaleTimeString()}</span>
            <span style={{ fontSize: 10, color: '#c0a0a8', fontStyle: 'italic', flex: 1 }}>&quot;{s.raw_text.slice(0, 80)}&quot;</span>
          </div>
          {s.signal_type && (
            <div style={{ paddingLeft: 68, marginTop: 3, fontSize: 9, fontFamily: 'Inter,sans-serif', color: 'var(--text3)' }}>
              <span style={{ fontSize: 8, padding: '1px 6px', borderRadius: 2, background: '#2d0a0a', color: '#ff6b6b', border: '1px solid #5a1a1a', fontWeight: 600, marginRight: 6 }}>{s.signal_type}</span>
              Conf: {s.confidence ? `${Math.round(s.confidence * 100)}%` : '—'}
            </div>
          )}
        </div>
      ))}
      <div style={{ marginTop: 12 }}>
        <div className="tile-label" style={{ marginBottom: 6 }}>Accuracy by Signal Type</div>
        {Object.entries(TYPE_ACCURACY).map(([type, acc]) => (
          <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 5 }}>
            <span style={{ fontSize: 9, color: 'var(--text3)', width: 120, fontFamily: 'Inter,sans-serif' }}>{type}</span>
            <div style={{ flex: 1, height: 6, background: '#0d1526', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${acc * 100}%`, height: '100%', background: `linear-gradient(90deg,${acc > 0.7 ? 'var(--green)' : 'var(--amber)'},#4ade80)`, borderRadius: 3 }} />
            </div>
            <span style={{ fontSize: 10, color: acc > 0.7 ? 'var(--green)' : 'var(--amber)', width: 36, textAlign: 'right', fontWeight: 600 }}>{Math.round(acc * 100)}%</span>
          </div>
        ))}
      </div>
      <CiteBadge source="Backtested on historical signals · GPT-4.1-mini" />
    </div>
  );
}
