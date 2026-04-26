'use client';
import { useEffect } from 'react';
import type { TrumpSignal, Prediction } from '@/lib/types';

interface Props {
  open: boolean;
  signal: TrumpSignal | null;
  prediction: Prediction | null;
  onClose: () => void;
}

export function SignalDetailModal({ open, signal, prediction, onClose }: Props) {
  useEffect(() => {
    if (!open) return;
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open, onClose]);

  if (!open || !signal) return null;

  return (
    <div onClick={e => { if (e.target === e.currentTarget) onClose(); }} style={{ position: 'fixed', inset: 0, background: '#00000099', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
      <div style={{ background: 'var(--bg3)', border: '1px solid var(--border)', borderRadius: 6, padding: 20, width: 640, maxWidth: '95vw', position: 'relative' }}>
        <div onClick={onClose} style={{ position: 'absolute', top: 12, right: 14, color: 'var(--text3)', cursor: 'pointer', fontSize: 16 }}>✕</div>
        <div style={{ color: 'var(--red)', fontSize: 14, fontWeight: 600, marginBottom: 4 }}>Signal Detail — {signal.signal_type ?? 'Classifying'}</div>
        <div style={{ fontSize: 10, color: 'var(--text3)', fontFamily: 'Inter,sans-serif', marginBottom: 12 }}>{signal.source} · {new Date(signal.posted_at).toLocaleString()}</div>
        <div style={{ fontSize: 12, color: '#e8c0c8', fontStyle: 'italic', borderLeft: '2px solid #7f1d1d', paddingLeft: 12, marginBottom: 16, lineHeight: 1.6 }}>&quot;{signal.raw_text}&quot;</div>
        {signal.llm_reasoning && <div style={{ fontSize: 10, color: 'var(--text3)', fontFamily: 'Inter,sans-serif', marginBottom: 12 }}><strong style={{ color: 'var(--text2)' }}>AI Reasoning:</strong> {signal.llm_reasoning}</div>}
        {prediction && (
          <div>
            <div style={{ fontSize: 9, color: '#1a5a3a', textTransform: 'uppercase', letterSpacing: 1.5, fontFamily: 'Inter,sans-serif', fontWeight: 700, marginBottom: 8 }}>Algorithm Call</div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {prediction.buy_list.map(b => <span key={b.ticker} style={{ padding: '3px 10px', background: '#071a0f', border: '1px solid #0d3a1e', borderRadius: 3, color: 'var(--green)', fontSize: 11, fontWeight: 600 }}>BUY {b.ticker}</span>)}
              {prediction.short_list.map(s => <span key={s.ticker} style={{ padding: '3px 10px', background: '#1a0707', border: '1px solid #3a0d0d', borderRadius: 3, color: 'var(--red)', fontSize: 11, fontWeight: 600 }}>SHORT {s.ticker}</span>)}
            </div>
            <div style={{ fontSize: 8, color: '#1a3a2a', fontFamily: 'Inter,sans-serif', marginTop: 8 }}>Confidence: {Math.round(prediction.confidence * 100)}% · Horizon: {prediction.horizon_days} days · GPT-4.1-mini + Quant</div>
          </div>
        )}
      </div>
    </div>
  );
}
