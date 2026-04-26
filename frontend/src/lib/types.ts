export interface Quote {
  symbol: string;
  price: number;
  change_pct: number;
  volume: number | null;
  source: string;
  fetched_at: string;
}

export interface TrumpSignal {
  id: number;
  raw_text: string;
  source: string;
  signal_type: string | null;
  confidence: number | null;
  affected_tickers: string[] | null;
  affected_sectors: string[] | null;
  llm_reasoning: string | null;
  posted_at: string;
}

export interface Prediction {
  id: number;
  signal_id: number;
  buy_list: { ticker: string; reason: string }[];
  short_list: { ticker: string; reason: string }[];
  reasoning: string;
  confidence: number;
  horizon_days: number;
  created_at: string;
}

export interface NewsArticle {
  id: number;
  headline: string;
  source: string;
  url: string;
  published_at: string;
  tags: string[] | null;
}

export interface AlertPayload {
  type: 'alert';
  signal_type: string;
  signal_text: string;
  source: string;
  buy_list: { ticker: string; reason: string }[];
  short_list: { ticker: string; reason: string }[];
  reasoning: string;
  confidence: number;
  horizon_days: number;
}
