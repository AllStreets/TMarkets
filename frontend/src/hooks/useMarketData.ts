'use client';
import { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import type { Quote, TrumpSignal, Prediction, NewsArticle } from '@/lib/types';

export function useMarketData() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [signal, setSignal] = useState<TrumpSignal | null>(null);
  const [signalHistory, setSignalHistory] = useState<TrumpSignal[]>([]);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [news, setNews] = useState<NewsArticle[]>([]);

  const refresh = useCallback(async () => {
    const [q, s, sh, p, n] = await Promise.allSettled([
      api.quotes(), api.latestSignal(), api.signalHistory(), api.latestPrediction(), api.newsFeed(),
    ]);
    if (q.status === 'fulfilled') setQuotes(q.value);
    if (s.status === 'fulfilled') setSignal(s.value as TrumpSignal);
    if (sh.status === 'fulfilled') setSignalHistory(sh.value as TrumpSignal[]);
    if (p.status === 'fulfilled') setPrediction(p.value as Prediction);
    if (n.status === 'fulfilled') setNews(n.value as NewsArticle[]);
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 60_000);
    return () => clearInterval(interval);
  }, [refresh]);

  return { quotes, signal, signalHistory, prediction, news, refresh };
}
