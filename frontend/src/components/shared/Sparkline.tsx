'use client';
import { useId } from 'react';

interface SparklineProps {
  data: number[];
  color: string;
  height?: number;
}

export function Sparkline({ data, color, height = 44 }: SparklineProps) {
  const uid = useId().replace(/:/g, '');
  if (data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const w = 100;
  const h = height;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - ((v - min) / range) * (h - 4) - 2}`).join(' ');
  const areaD = `M${pts.split(' ').join(' L')} L${w},${h} L0,${h} Z`;
  const lineD = `M${pts.split(' ').join(' L')}`;
  const id = `grad-${uid}`;

  return (
    <svg width="100%" height={height} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none">
      <defs>
        <linearGradient id={id} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.25} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <path d={areaD} fill={`url(#${id})`} />
      <path d={lineD} fill="none" stroke={color} strokeWidth={1.5} />
    </svg>
  );
}
