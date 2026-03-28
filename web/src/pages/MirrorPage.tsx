import { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import DeliberationPanel from '../components/DeliberationPanel';
import DeliberationTrigger from '../components/DeliberationTrigger';
import MirrorInput from '../components/MirrorInput';
import MirrorReport from '../components/MirrorReport';
import { API_BASE } from '../services/api';
import type { MirrorInput as MirrorInputType, MirrorReport as MirrorReportType } from '../services/api';

const STEPS = [
  { key: 'mirror', zh: '照妖翻译 + 妖怪检测', en: 'Mirror Translation + Monster Detection' },
  { key: 'scoring', zh: '评分 + 生成建议', en: 'Scoring + Recommendations' },
];

function MirrorPage() {
  const { t, i18n } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<MirrorReportType | null>(null);
  const [lastContent, setLastContent] = useState('');
  const [deliberation, setDeliberation] = useState<any>(null);
  const [currentStep, setCurrentStep] = useState('');
  const [elapsedSecs, setElapsedSecs] = useState(0);

  const language: 'zh' | 'en' = i18n.language === 'en' ? 'en' : 'zh';

  const handleSubmit = useCallback(async (input: MirrorInputType) => {
    setLoading(true);
    setError(null);
    setReport(null);
    setDeliberation(null);
    setLastContent(input.content);
    setCurrentStep('');
    setElapsedSecs(0);

    const startTime = Date.now();
    const timer = setInterval(() => {
      setElapsedSecs(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    try {
      const resp = await fetch(`${API_BASE}/api/mirror/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });

      if (!resp.ok) throw new Error(`API error: ${resp.status}`);
      if (!resp.body) throw new Error('No response body');

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      const partialReport: MirrorReportType = {
        translations: [],
        monsters_detected: [],
        xray: null,
        health_score: null,
        recommendations: [],
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let eventType = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith('data: ') && eventType) {
            try {
              const data = JSON.parse(line.slice(6));
              if (eventType === 'status') {
                setCurrentStep(data.step);
              } else if (eventType === 'mirror') {
                partialReport.translations = data.translations || [];
                partialReport.monsters_detected = data.monsters_detected || [];
                setReport({ ...partialReport });
              } else if (eventType === 'health') {
                partialReport.health_score = data.health_score || null;
                setReport({ ...partialReport });
              } else if (eventType === 'recommendations') {
                partialReport.recommendations = data.recommendations || [];
                setReport({ ...partialReport });
              } else if (eventType === 'error') {
                setError(`${data.step}: ${data.message}`);
              }
            } catch {
              // skip malformed data
            }
            eventType = '';
          }
        }
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      clearInterval(timer);
      setLoading(false);
      setCurrentStep('');
    }
  }, []);

  const stepLabel = STEPS.find(s => s.key === currentStep);

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>{t('app_name')}</h1>
        <p style={styles.tagline}>{t('tagline')}</p>
      </div>

      <MirrorInput onSubmit={handleSubmit} loading={loading} />

      {error && <div style={styles.error}>{error}</div>}

      {loading && (
        <div style={styles.loadingBox}>
          <span style={styles.spinner} />
          <div>
            <div style={{ fontWeight: 500 }}>
              {stepLabel ? (language === 'zh' ? stepLabel.zh : stepLabel.en) : (language === 'zh' ? '准备中...' : 'Preparing...')}
            </div>
            <div style={{ fontSize: 13, color: '#9ca3af', marginTop: 4 }}>
              {elapsedSecs}s
            </div>
          </div>
        </div>
      )}

      {report && report.translations.length > 0 && (
        <>
          <MirrorReport report={report} language={language} />
          {!loading && (
            <DeliberationTrigger content={lastContent} onResult={setDeliberation} />
          )}
        </>
      )}

      {deliberation && (
        <DeliberationPanel
          deliberation={deliberation.deliberation}
          advocatePositions={deliberation.advocate_positions}
          roundsCompleted={deliberation.rounds_completed}
        />
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: 'flex', flexDirection: 'column', gap: '28px',
    padding: '24px 32px 48px', maxWidth: '960px', margin: '0 auto',
    width: '100%', boxSizing: 'border-box',
  },
  header: { textAlign: 'center' },
  title: {
    fontSize: '36px', fontWeight: 700, color: 'var(--text-h)',
    margin: '0 0 8px', letterSpacing: '-0.5px',
  },
  tagline: { fontSize: '16px', color: 'var(--text)', margin: 0 },
  error: {
    padding: '12px 16px', borderRadius: '8px',
    background: '#fee2e2', color: '#991b1b', fontSize: '14px',
  },
  loadingBox: {
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    gap: '12px', padding: '24px', color: 'var(--text)', fontSize: '15px',
  },
  spinner: {
    width: '20px', height: '20px',
    border: '3px solid var(--border)', borderTopColor: 'var(--accent)',
    borderRadius: '50%', animation: 'spin 0.8s linear infinite',
  },
};

export default MirrorPage;
