import type { Quote } from '@/lib/types';
import { CiteBadge } from '@/components/shared/CiteBadge';

interface IndexTileProps {
  quote: Quote;
  onClick: (quote: Quote) => void;
}

export function IndexTile({ quote, onClick }: IndexTileProps) {
  const up = quote.change_pct >= 0;
  const accentColor = up ? 'var(--green)' : 'var(--red)';

  return (
    <div
      className="tile"
      onClick={() => onClick(quote)}
      style={{ cursor: 'pointer' }}
    >
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, ${accentColor}, transparent)`, borderRadius: '4px 4px 0 0' }} />
      <div className="tile-label">{quote.symbol}</div>
      <div className="tile-val">{quote.price.toLocaleString('en-US', { maximumFractionDigits: 2 })}</div>
      <div className={`tile-change ${up ? 'up' : 'dn'}`}>
        {up ? '▲' : '▼'} {Math.abs(quote.change_pct).toFixed(2)}%
      </div>
      <CiteBadge source={quote.source} />
    </div>
  );
}
