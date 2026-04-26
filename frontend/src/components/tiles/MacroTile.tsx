import { CiteBadge } from '@/components/shared/CiteBadge';

interface MacroTileProps {
  label: string;
  value: string;
  sub: string;
  color?: string;
  source: string;
  onClick: () => void;
}

export function MacroTile({ label, value, sub, color = 'var(--text)', source, onClick }: MacroTileProps) {
  return (
    <div className="tile tile-neutral" onClick={onClick}>
      <div className="tile-label">{label}</div>
      <div className="tile-val" style={{ color }}>{value}</div>
      <div className="tile-change" style={{ color: 'var(--text3)' }}>{sub}</div>
      <CiteBadge source={source} />
    </div>
  );
}
