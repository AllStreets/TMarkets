import type { Quote } from '@/lib/types';
import { CiteBadge } from '@/components/shared/CiteBadge';

const SECTOR_ETFS: Record<string, string> = {
  Technology: 'XLK', Energy: 'XLE', 'Consumer Disc': 'XLY', Defense: 'XAR',
  Semis: 'SOXX', Materials: 'XLB', Financials: 'XLF', Utilities: 'XLU',
};

interface Props { quotes: Quote[]; onSectorClick: (etf: string) => void; }

export function HeatmapTile({ quotes, onSectorClick }: Props) {
  const quoteMap = Object.fromEntries(quotes.map(q => [q.symbol, q]));
  const sectors = Object.entries(SECTOR_ETFS);

  return (
    <div className="tile" style={{ padding: '11px 13px' }}>
      <div className="tile-label">Sector Heatmap</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 4, marginTop: 8 }}>
        {sectors.map(([name, etf]) => {
          const q = quoteMap[etf];
          const pct = q?.change_pct ?? 0;
          const pos = pct > 0;
          return (
            <div
              key={name}
              onClick={() => onSectorClick(etf)}
              style={{ borderRadius: 3, padding: '5px 7px', fontSize: 9, fontFamily: 'Inter,sans-serif', fontWeight: 600, cursor: 'pointer', transition: 'filter .15s', background: pos ? '#071a0f' : '#1a0707', border: `1px solid ${pos ? '#0d3a1e' : '#3a0d0d'}`, color: pos ? 'var(--green)' : 'var(--red)' }}
              onMouseEnter={e => (e.currentTarget.style.filter = 'brightness(1.3)')}
              onMouseLeave={e => (e.currentTarget.style.filter = '')}
            >
              <span style={{ display: 'block', marginBottom: 1 }}>{name}</span>
              <span style={{ fontSize: 11, fontWeight: 700 }}>{pct >= 0 ? '+' : ''}{pct.toFixed(2)}%</span>
            </div>
          );
        })}
      </div>
      <CiteBadge source="yfinance · GICS" />
    </div>
  );
}
