'use client';
import type { NewsArticle } from '@/lib/types';
import { CiteBadge } from '@/components/shared/CiteBadge';

interface Props { title: string; articles: NewsArticle[]; source: string; }

export function NewsTile({ title, articles, source }: Props) {
  return (
    <div style={{ background: 'linear-gradient(135deg,#090d1a,#070a14)', border: '1px solid #0f1a30', borderRadius: 4, padding: '9px 11px' }}>
      <div className="tile-label" style={{ color: '#1a3a6a', marginBottom: 6 }}>{title}</div>
      {articles.map((a) => (
        <div key={a.id} onClick={() => window.open(a.url, '_blank')} style={{ display: 'flex', alignItems: 'flex-start', gap: 7, padding: '6px 0', borderBottom: '1px solid var(--border2)', cursor: 'pointer' }}
          onMouseEnter={e => { (e.currentTarget.querySelector('.nt') as HTMLElement).style.color = '#7aaddd'; }}
          onMouseLeave={e => { (e.currentTarget.querySelector('.nt') as HTMLElement).style.color = '#4a7aaa'; }}
        >
          <span style={{ color: '#1a3a5a', fontSize: 9, flexShrink: 0, marginTop: 1 }}>→</span>
          <div>
            <div className="nt" style={{ fontSize: 10, color: '#4a7aaa', fontFamily: 'Inter,sans-serif', lineHeight: 1.4, transition: 'color .15s' }}>{a.headline}</div>
            <div style={{ fontSize: 8, color: 'var(--text4)', marginTop: 2, fontFamily: 'Inter,sans-serif' }}>{a.source} · {new Date(a.published_at).toLocaleTimeString()}</div>
          </div>
        </div>
      ))}
      <CiteBadge source={source} />
    </div>
  );
}
