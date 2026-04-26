'use client';
import { useState, useEffect } from 'react';
import type { AlertPayload } from '@/lib/types';

interface Props { alert: AlertPayload | null; }

export function AlertBanner({ alert }: Props) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (alert) {
      setVisible(true);
      const t = setTimeout(() => setVisible(false), 12000);
      return () => clearTimeout(t);
    }
  }, [alert]);

  if (!visible || !alert) return null;

  return (
    <div style={{ position: 'fixed', bottom: 20, right: 20, zIndex: 500, background: '#0e060c', border: '1px solid #ff4d6d', borderRadius: 6, padding: '12px 16px', maxWidth: 380, boxShadow: '0 0 24px #ff4d6d30' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ fontSize: 9, color: 'var(--red)', fontWeight: 700, letterSpacing: 1.5, fontFamily: 'Inter,sans-serif', textTransform: 'uppercase' }}>⚡ AI Alert · {alert.signal_type}</span>
        <span onClick={() => setVisible(false)} style={{ cursor: 'pointer', color: 'var(--text3)', fontSize: 13 }}>✕</span>
      </div>
      <div style={{ fontSize: 10, color: '#e8c0c8', marginBottom: 8, fontStyle: 'italic' }}>&quot;{alert.signal_text.slice(0, 100)}&quot;</div>
      <div style={{ fontSize: 10 }}>
        {(alert.buy_list ?? []).length > 0 && <span style={{ color: 'var(--green)', fontWeight: 600 }}>BUY: {(alert.buy_list ?? []).map(b => b.ticker).join(', ')}</span>}
        {(alert.buy_list ?? []).length > 0 && (alert.short_list ?? []).length > 0 && ' · '}
        {(alert.short_list ?? []).length > 0 && <span style={{ color: 'var(--red)', fontWeight: 600 }}>SHORT: {(alert.short_list ?? []).map(s => s.ticker).join(', ')}</span>}
      </div>
      <div style={{ fontSize: 8, color: '#1a3a2a', fontFamily: 'Inter,sans-serif', marginTop: 4 }}>
        Confidence: {Math.round(alert.confidence * 100)}%
      </div>
    </div>
  );
}
