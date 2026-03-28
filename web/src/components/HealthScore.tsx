import { useTranslation } from 'react-i18next';
import type { HealthScore as HealthScoreType } from '../services/api';

interface HealthScoreProps {
  score: HealthScoreType;
}

function getScoreColor(value: number): string {
  if (value >= 70) return '#16a34a';
  if (value >= 40) return '#ca8a04';
  return '#dc2626';
}

const DIMENSION_KEYS = ['clarity', 'accountability', 'momentum', 'trust'] as const;

function HealthScore({ score }: HealthScoreProps) {
  const { t } = useTranslation();
  const overallColor = getScoreColor(score.overall);

  return (
    <div style={styles.container}>
      <div style={styles.overallSection}>
        <span
          style={{
            ...styles.overallScore,
            color: overallColor,
          }}
        >
          {score.overall}
        </span>
        <span style={styles.overallLabel}>{t('health_score_overall')}</span>
      </div>

      <div style={styles.dimensions}>
        {DIMENSION_KEYS.map((dim) => {
          const value = score.dimensions[dim];
          const color = getScoreColor(value);
          return (
            <div key={dim} style={styles.dimensionRow}>
              <div style={styles.dimensionHeader}>
                <span style={styles.dimensionLabel}>{t(`dimension_${dim}`)}</span>
                <span style={{ ...styles.dimensionValue, color }}>{value}</span>
              </div>
              <div style={styles.barTrack}>
                <div
                  style={{
                    ...styles.barFill,
                    width: `${value}%`,
                    background: color,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    gap: '32px',
    alignItems: 'center',
    padding: '24px',
    border: '1px solid var(--border)',
    borderRadius: '12px',
    background: 'var(--bg)',
    textAlign: 'left',
  },
  overallSection: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '100px',
  },
  overallScore: {
    fontSize: '56px',
    fontWeight: 700,
    lineHeight: 1,
    fontFamily: 'var(--heading)',
  },
  overallLabel: {
    fontSize: '14px',
    color: 'var(--text)',
    marginTop: '6px',
  },
  dimensions: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  dimensionRow: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  dimensionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dimensionLabel: {
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--text-h)',
  },
  dimensionValue: {
    fontSize: '14px',
    fontWeight: 600,
  },
  barTrack: {
    height: '8px',
    borderRadius: '4px',
    background: 'var(--border)',
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: '4px',
    transition: 'width 0.5s ease',
  },
};

export default HealthScore;
