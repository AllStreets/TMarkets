import type { Quote } from '@/lib/types';
import { Sparkline } from '@/components/shared/Sparkline';
import { CiteBadge } from '@/components/shared/CiteBadge';

interface ChartTileProps {
  quote: Quote;
  history: number[];
  onClick: (quote: Quote) => void;
}

export function ChartTile({ quote, history, onClick }: ChartTileProps) {
  const up = quote.change_pct >= 0;
  const color = up ? 'var(--green)' : 'var(--red)';

  return (
    <div
      onClick={() => onClick(quote)}
      style={{ background: 'linear-gradient(135deg,var(--bg3),var(--bg4))', border: '1px solid var(--border)', borderRadius: 4, padding: '9px 11px 7px', cursor: 'pointer', transition: 'border-color .2s' }}
      onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--cyan)')}
      onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text2)' }}>{quote.symbol}</span>
        <span style={{ fontSize: 11, fontWeight: 600, color }}>{quote.price.toFixed(2)} {up ? '▲' : '▼'}{Math.abs(quote.change_pct).toFixed(2)}%</span>
      </div>
      <Sparkline data={history} color={color} />
      <CiteBadge source={`↗ click · ${quote.source}`} />
    </div>
  );
}
