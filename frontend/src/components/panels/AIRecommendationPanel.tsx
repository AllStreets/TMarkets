'use client';
import type { Prediction } from '@/lib/types';

interface Props { prediction: Prediction | null; }

export function AIRecommendationPanel({ prediction }: Props) {
  if (!prediction) return (
    <div style={{ background: 'linear-gradient(135deg,#070e0c,#050c09)', border: '1px solid #0d2a1e', borderRadius: 4, padding: '11px 13px' }}>
      <div style={{ fontSize: 8.5, color: '#1a5a3a', textTransform: 'uppercase', letterSpacing: 1.5, fontFamily: 'Inter,sans-serif', fontWeight: 700 }}>🤖 AI CALL — Awaiting signal…</div>
    </div>
  );

  const confPct = Math.round(prediction.confidence * 100);

  return (
    <div style={{ background: 'linear-gradient(135deg,#070e0c,#050c09)', border: '1px solid #0d2a1e', borderRadius: 4, padding: '11px 13px', position: 'relative', overflow: 'hidden' }}>
      <div style={{ fontSize: 8.5, color: '#1a5a3a', textTransform: 'uppercase', letterSpacing: 1.5, fontFamily: 'Inter,sans-serif', fontWeight: 700, marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
        <span style={{ width: 5, height: 5, background: 'var(--green)', borderRadius: '50%', boxShadow: '0 0 8px var(--green)', display: 'inline-block' }} />
        AI Call · GPT-4.1-mini + Quant
      </div>
      {prediction.buy_list.map((b) => (
        <div key={b.ticker} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, padding: '5px 8px', borderRadius: 3, background: '#071a0f', border: '1px solid #0d3a1e' }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 1, fontFamily: 'Inter,sans-serif', color: 'var(--green)', width: 32 }}>BUY</span>
          <span style={{ fontSize: 12, fontWeight: 600 }}>{b.ticker}</span>
          <span style={{ fontSize: 9, color: '#3a5a4a', fontFamily: 'Inter,sans-serif', marginLeft: 'auto', textAlign: 'right' }}>{b.reason}</span>
        </div>
      ))}
      {prediction.short_list.map((s) => (
        <div key={s.ticker} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, padding: '5px 8px', borderRadius: 3, background: '#1a0707', border: '1px solid #3a0d0d' }}>
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 1, fontFamily: 'Inter,sans-serif', color: 'var(--red)', width: 32 }}>SHORT</span>
          <span style={{ fontSize: 12, fontWeight: 600 }}>{s.ticker}</span>
          <span style={{ fontSize: 9, color: '#5a3a3a', fontFamily: 'Inter,sans-serif', marginLeft: 'auto', textAlign: 'right' }}>{s.reason}</span>
        </div>
      ))}
      <div style={{ height: 3, background: '#0d2a1e', borderRadius: 2, marginTop: 8, overflow: 'hidden' }}>
        <div style={{ width: `${confPct}%`, height: '100%', background: 'linear-gradient(90deg,var(--green),#4ade80)', borderRadius: 2, boxShadow: '0 0 6px #00e67660' }} />
      </div>
      <div style={{ fontSize: 8, color: '#1a3a2a', fontFamily: 'Inter,sans-serif', marginTop: 6 }}>
        Confidence: {confPct}% · Horizon: {prediction.horizon_days} days
      </div>
    </div>
  );
}
