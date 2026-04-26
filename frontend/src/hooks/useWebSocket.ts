'use client';
import { useEffect, useRef, useCallback } from 'react';

export function useWebSocket(onMessage: (data: unknown) => void) {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    const url = (process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000') + '/ws';
    ws.current = new WebSocket(url);
    ws.current.onmessage = (e) => {
      try { onMessage(JSON.parse(e.data)); } catch { /* ignore */ }
    };
    ws.current.onclose = () => {
      reconnectTimeout.current = setTimeout(connect, 3000);
    };
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => {
      ws.current?.close();
      clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);
}
