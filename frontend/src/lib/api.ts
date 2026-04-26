const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { next: { revalidate: 30 } });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  quotes: () => get<import('./types').Quote[]>('/api/market/quotes'),
  latestSignal: () => get<import('./types').TrumpSignal>('/api/signals/latest'),
  signalHistory: (limit = 10) => get<import('./types').TrumpSignal[]>(`/api/signals/history?limit=${limit}`),
  latestPrediction: () => get<import('./types').Prediction>('/api/predictions/latest'),
  newsFeed: (limit = 30) => get<import('./types').NewsArticle[]>(`/api/news/feed?limit=${limit}`),
};
