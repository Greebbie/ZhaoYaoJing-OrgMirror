import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

interface DashboardData {
  health_score_avg: number | null;
  total_analyses: number;
  total_items: number;
  monster_counts: Record<string, number>;
  top_monsters: { monster_id: string; count: number; severity_avg: number }[];
  risk_items: { id: string; name: string; status: string; days_stale: number }[];
  period: string;
}

import { API_BASE } from '../services/api';

function scoreColor(score: number | null): string {
  if (score === null) return '#9ca3af';
  if (score >= 70) return '#22c55e';
  if (score >= 40) return '#eab308';
  return '#ef4444';
}

function severityColor(sev: number): string {
  if (sev < 1.5) return '#22c55e';
  if (sev < 2.5) return '#eab308';
  if (sev < 3.5) return '#ef4444';
  return '#7c3aed';
}

function DashboardPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    (async () => {
      try {
        const resp = await fetch(`${API_BASE}/api/dashboard/summary?days=7`);
        if (!resp.ok) throw new Error(`${resp.status}`);
        setData(await resp.json());
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : 'Failed to load');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div style={{ textAlign: 'center', padding: 40 }}>{t('loading')}</div>;
  if (error) return <div style={{ color: '#ef4444', padding: 20 }}>Error: {error}</div>;
  if (!data) return null;

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 32px' }}>
      <h1 style={{ marginBottom: 4 }}>{t('dashboard_title')}</h1>
      <p style={{ color: '#6b7280', marginTop: 0, marginBottom: 24 }}>
        {t('dashboard_period', { period: data.period })}
      </p>

      {/* Top metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 24 }}>
        <div style={cardStyle}>
          <div style={{ fontSize: 13, color: '#6b7280' }}>{t('health_score')}</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: scoreColor(data.health_score_avg) }}>
            {data.health_score_avg !== null ? Math.round(data.health_score_avg) : '—'}
          </div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontSize: 13, color: '#6b7280' }}>{t('analyses')}</div>
          <div style={{ fontSize: 36, fontWeight: 700 }}>{data.total_analyses}</div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontSize: 13, color: '#6b7280' }}>{t('tracked_items')}</div>
          <div style={{ fontSize: 36, fontWeight: 700 }}>{data.total_items}</div>
        </div>
      </div>

      {/* Monster ranking */}
      <div style={{ ...cardStyle, marginBottom: 24 }}>
        <h3 style={{ marginTop: 0 }}>{t('monster_ranking')}</h3>
        {data.top_monsters.length === 0 ? (
          <p style={{ color: '#9ca3af' }}>{t('no_data')}</p>
        ) : (
          data.top_monsters.map((m, i) => (
            <div key={m.monster_id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0', borderBottom: i < data.top_monsters.length - 1 ? '1px solid #f3f4f6' : 'none' }}>
              <span style={{ minWidth: 20, color: '#9ca3af', fontSize: 13 }}>{i + 1}.</span>
              <span style={{ flex: 1, fontWeight: 500 }}>{m.monster_id}</span>
              <span style={{ fontSize: 13, color: '#6b7280' }}>
                {m.count} {t('times')}
              </span>
              <div style={{ width: 80, height: 8, background: '#f3f4f6', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${Math.min(m.count * 10, 100)}%`, background: severityColor(m.severity_avg), borderRadius: 4 }} />
              </div>
            </div>
          ))
        )}
      </div>

      {/* Risk items */}
      <div style={cardStyle}>
        <h3 style={{ marginTop: 0 }}>{t('risk_items')}</h3>
        {data.risk_items.length === 0 ? (
          <p style={{ color: '#9ca3af' }}>{t('no_risk_items')}</p>
        ) : (
          data.risk_items.map((item) => (
            <div key={item.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '8px 0', borderBottom: '1px solid #f3f4f6' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: item.days_stale > 14 ? '#ef4444' : item.days_stale > 7 ? '#eab308' : '#22c55e', flexShrink: 0 }} />
              <span style={{ flex: 1, fontWeight: 500 }}>{item.name}</span>
              <span style={{ fontSize: 13, color: '#6b7280' }}>
                {item.days_stale} {t('days_stale')}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: 'white',
  border: '1px solid #e5e7eb',
  borderRadius: 12,
  padding: 20,
};

export default DashboardPage;
