'use client';
import type { TrumpSignal } from '@/lib/types';
import { CiteBadge } from '@/components/shared/CiteBadge';

interface Props { signal: TrumpSignal | null; onClick: (s: TrumpSignal) => void; }

export function TrumpSignalPanel({ signal, onClick }: Props) {
  if (!signal) return <div className="tile" style={{ background: 'linear-gradient(135deg,#130810,#0e060c)', border: '1px solid #2d0a1a' }}><div className="tile-label" style={{ color: '#7f2a3a' }}>⚡ TRUMP SIGNAL — Awaiting signal…</div></div>;

  return (
    <div onClick={() => onClick(signal)} style={{ background: 'linear-gradient(135deg,#130810,#0e060c)', border: '1px solid #2d0a1a', borderRadius: 4, padding: '11px 13px', cursor: 'pointer', transition: 'border-color .2s' }}
      onMouseEnter={e => (e.currentTarget.style.borderColor = '#5a1a2a')}
      onMouseLeave={e => (e.currentTarget.style.borderColor = '#2d0a1a')}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 8.5, color: '#7f2a3a', textTransform: 'uppercase', letterSpacing: 1.5, fontFamily: 'Inter,sans-serif', fontWeight: 700, marginBottom: 8 }}>
        <span style={{ width: 5, height: 5, background: 'var(--red)', borderRadius: '50%', boxShadow: '0 0 6px var(--red)', display: 'inline-block', animation: 'pulse 1.5s ease-in-out infinite' }} />
        Trump Signal Feed
      </div>
      <div style={{ fontSize: 11, color: '#e8c0c8', lineHeight: 1.55, fontStyle: 'italic', borderLeft: '2px solid #7f1d1d', paddingLeft: 10, marginBottom: 8 }}>
        &quot;{(signal.raw_text ?? '').slice(0, 200)}&quot;
      </div>
      <div style={{ fontSize: 9, color: '#4a2030', fontFamily: 'Inter,sans-serif' }}>
        <span style={{ color: '#7a3040' }}>{signal.source}</span> · {new Date(signal.posted_at).toLocaleTimeString()} · {signal.signal_type ?? 'Classifying…'}
      </div>
      <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap', marginTop: 8 }}>
        {signal.affected_sectors?.map(s => (
          <span key={s} style={{ fontSize: 8, padding: '2px 7px', borderRadius: 2, fontFamily: 'Inter,sans-serif', fontWeight: 600, letterSpacing: .5, textTransform: 'uppercase', background: '#2d1a00', color: '#ffa040', border: '1px solid #5a3000' }}>{s}</span>
        ))}
      </div>
      <CiteBadge source="Truth Social · WH Press · NewsAPI · GNews" />
    </div>
  );
}
