import { useTranslation } from 'react-i18next';
import type { MirrorReport as MirrorReportType } from '../services/api';
import MonsterCard from './MonsterCard';
import HealthScore from './HealthScore';

interface MirrorReportProps {
  report: MirrorReportType;
  language: 'zh' | 'en';
}

const MONSTER_ROW_COLORS: Record<string, string> = {
  'responsibility-diffusion': 'rgba(239, 68, 68, 0.08)',
  'fake-alignment': 'rgba(234, 179, 8, 0.08)',
  'progress-theater': 'rgba(168, 85, 247, 0.08)',
  'scope-fog': 'rgba(59, 130, 246, 0.08)',
  'default': 'transparent',
};

function getRowColor(monsterType: string | null): string {
  if (!monsterType) return MONSTER_ROW_COLORS['default'];
  return MONSTER_ROW_COLORS[monsterType] ?? 'rgba(168, 85, 247, 0.05)';
}

const PRIORITY_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
};

function MirrorReport({ report, language }: MirrorReportProps) {
  const { t } = useTranslation();

  const sortedRecommendations = [...report.recommendations].sort(
    (a, b) => (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99)
  );

  return (
    <div style={styles.report}>
      {/* Translation section */}
      {report.translations.length > 0 && (
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>{t('translations_title')}</h2>
          <div style={styles.translationTable}>
            <div style={styles.translationHeader}>
              <span style={styles.translationHeaderCell}>{t('original_text')}</span>
              <span style={styles.translationHeaderCell}>{t('mirror_translation')}</span>
            </div>
            {report.translations.map((tr, i) => (
              <div
                key={i}
                style={{
                  ...styles.translationRow,
                  background: getRowColor(tr.monster_type),
                }}
              >
                <div style={styles.translationCell}>{tr.original}</div>
                <div style={{ ...styles.translationCell, fontWeight: 500, color: 'var(--text-h)' }}>
                  {tr.mirror}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Monster section */}
      {report.monsters_detected.length > 0 && (
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>
            {t('monsters_title')} ({report.monsters_detected.length})
          </h2>
          <div style={styles.monsterGrid}>
            {report.monsters_detected.map((monster) => (
              <MonsterCard key={monster.monster_id} monster={monster} language={language} />
            ))}
          </div>
        </section>
      )}

      {/* Health Score section */}
      {report.health_score && (
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>{t('health_score_title')}</h2>
          <HealthScore score={report.health_score} />
        </section>
      )}

      {/* Recommendations section */}
      {sortedRecommendations.length > 0 && (
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>{t('recommendations_title')}</h2>
          <div style={styles.recList}>
            {sortedRecommendations.map((rec, i) => (
              <div key={i} style={styles.recCard}>
                <div style={styles.recHeader}>
                  <span style={styles.recPriority}>{rec.priority.toUpperCase()}</span>
                  <span style={styles.recAction}>
                    {language === 'zh' ? rec.action_zh : rec.action_en}
                  </span>
                </div>
                <p style={styles.recRationale}>
                  {language === 'zh' ? rec.rationale_zh : rec.rationale_en}
                </p>
                {rec.addressed_monsters.length > 0 && (
                  <div style={styles.recMonsters}>
                    {rec.addressed_monsters.map((m) => (
                      <span key={m} style={styles.recMonsterTag}>{m}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  report: {
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
    width: '100%',
    textAlign: 'left',
  },
  section: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 600,
    color: 'var(--text-h)',
    margin: 0,
    paddingBottom: '8px',
    borderBottom: '2px solid var(--accent)',
  },
  translationTable: {
    border: '1px solid var(--border)',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  translationHeader: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    background: 'var(--code-bg)',
    padding: '10px 16px',
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--text-h)',
    borderBottom: '1px solid var(--border)',
  },
  translationHeaderCell: {
    /* inherits from parent */
  },
  translationRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    padding: '12px 16px',
    borderBottom: '1px solid var(--border)',
    gap: '16px',
  },
  translationCell: {
    fontSize: '15px',
    lineHeight: '1.5',
    color: 'var(--text)',
  },
  monsterGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))',
    gap: '16px',
  },
  recList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  recCard: {
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '16px',
    background: 'var(--bg)',
  },
  recHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '8px',
  },
  recPriority: {
    fontSize: '11px',
    fontWeight: 700,
    padding: '2px 8px',
    borderRadius: '4px',
    background: 'var(--accent-bg)',
    color: 'var(--accent)',
    letterSpacing: '0.5px',
  },
  recAction: {
    fontSize: '16px',
    fontWeight: 600,
    color: 'var(--text-h)',
  },
  recRationale: {
    fontSize: '14px',
    lineHeight: '1.5',
    color: 'var(--text)',
    margin: '0 0 8px',
  },
  recMonsters: {
    display: 'flex',
    gap: '6px',
    flexWrap: 'wrap',
  },
  recMonsterTag: {
    fontSize: '12px',
    padding: '2px 8px',
    borderRadius: '4px',
    background: 'var(--code-bg)',
    color: 'var(--text)',
  },
};

export default MirrorReport;
