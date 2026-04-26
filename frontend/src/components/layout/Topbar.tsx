'use client';
import { useEffect, useState } from 'react';

export function Topbar({ alertCount }: { alertCount: number }) {
  const [time, setTime] = useState('');

  useEffect(() => {
    const tick = () => setTime(new Date().toLocaleTimeString('en-US', { timeZone: 'America/New_York', hour12: false }));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 16px', height: 36, background: 'var(--bg2)',
      borderBottom: '1px solid var(--border2)', position: 'sticky', top: 0, zIndex: 100,
    }}>
      <div style={{ fontFamily: 'Inter,sans-serif', fontWeight: 700, fontSize: 13, letterSpacing: 3, color: 'var(--cyan)', textShadow: '0 0 20px #00d4ff55' }}>
        TMARKETS
      </div>
      <div style={{ display: 'flex', gap: 20, fontSize: 10, color: '#5a7a9a', fontFamily: 'Inter,sans-serif' }}>
        <span>
          <span style={{ display: 'inline-block', width: 6, height: 6, background: 'var(--green)', borderRadius: '50%', marginRight: 5, boxShadow: '0 0 6px var(--green)', animation: 'pulse 1.5s infinite' }} />
          LIVE
        </span>
        <span>NYSE · {time} EST</span>
        {alertCount > 0 && <span>ALERTS: <span style={{ color: 'var(--red)', fontWeight: 600 }}>{alertCount} ACTIVE</span></span>}
        <span>ALGO: <span style={{ color: 'var(--green)' }}>RUNNING</span></span>
      </div>
    </div>
  );
}
