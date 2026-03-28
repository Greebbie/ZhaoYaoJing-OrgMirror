import { useTranslation } from 'react-i18next';
import type { MonsterDetected } from '../services/api';

interface MonsterCardProps {
  monster: MonsterDetected;
  language: 'zh' | 'en';
}

const SEVERITY_COLORS: Record<number, { bg: string; text: string; label_zh: string; label_en: string }> = {
  1: { bg: '#dcfce7', text: '#166534', label_zh: '轻微', label_en: 'Low' },
  2: { bg: '#fef9c3', text: '#854d0e', label_zh: '中等', label_en: 'Medium' },
  3: { bg: '#fee2e2', text: '#991b1b', label_zh: '严重', label_en: 'High' },
  4: { bg: '#f3e8ff', text: '#6b21a8', label_zh: '危险', label_en: 'Critical' },
};

function MonsterCard({ monster, language }: MonsterCardProps) {
  const { t } = useTranslation();
  const severityInfo = SEVERITY_COLORS[monster.severity] ?? SEVERITY_COLORS[2];
  const name = language === 'zh' ? monster.monster_name_zh : monster.monster_name_en;
  const explanation = language === 'zh' ? monster.explanation_zh : monster.explanation_en;
  const severityLabel = language === 'zh' ? severityInfo.label_zh : severityInfo.label_en;

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <span style={styles.emoji}>{monster.emoji}</span>
        <div style={styles.nameBlock}>
          <span style={styles.name}>{name}</span>
          <span style={styles.subName}>
            {language === 'zh' ? monster.monster_name_en : monster.monster_name_zh}
          </span>
        </div>
        <span
          style={{
            ...styles.badge,
            background: severityInfo.bg,
            color: severityInfo.text,
          }}
        >
          {severityLabel}
        </span>
      </div>

      <p style={styles.explanation}>{explanation}</p>

      {monster.evidence.length > 0 && (
        <div style={styles.evidenceSection}>
          <span style={styles.evidenceLabel}>{t('evidence')}</span>
          <ul style={styles.evidenceList}>
            {monster.evidence.map((e, i) => (
              <li key={i} style={styles.evidenceItem}>
                &ldquo;{e}&rdquo;
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={styles.confidenceSection}>
        <span style={styles.confidenceLabel}>
          {t('confidence')}: {Math.round(monster.confidence * 100)}%
        </span>
        <div style={styles.confidenceTrack}>
          <div
            style={{
              ...styles.confidenceFill,
              width: `${monster.confidence * 100}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: {
    border: '1px solid var(--border)',
    borderRadius: '12px',
    padding: '20px',
    background: 'var(--bg)',
    textAlign: 'left',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  emoji: {
    fontSize: '32px',
    lineHeight: 1,
  },
  nameBlock: {
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
  },
  name: {
    fontSize: '18px',
    fontWeight: 600,
    color: 'var(--text-h)',
  },
  subName: {
    fontSize: '13px',
    color: 'var(--text)',
  },
  badge: {
    padding: '4px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 600,
    whiteSpace: 'nowrap',
  },
  explanation: {
    fontSize: '15px',
    lineHeight: '1.6',
    color: 'var(--text)',
    margin: '0 0 12px',
  },
  evidenceSection: {
    marginBottom: '12px',
  },
  evidenceLabel: {
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--text-h)',
    display: 'block',
    marginBottom: '6px',
  },
  evidenceList: {
    margin: 0,
    paddingLeft: '18px',
  },
  evidenceItem: {
    fontSize: '14px',
    color: 'var(--text)',
    lineHeight: '1.5',
    fontStyle: 'italic',
    marginBottom: '4px',
  },
  confidenceSection: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  confidenceLabel: {
    fontSize: '13px',
    color: 'var(--text)',
    whiteSpace: 'nowrap',
  },
  confidenceTrack: {
    flex: 1,
    height: '6px',
    borderRadius: '3px',
    background: 'var(--border)',
    overflow: 'hidden',
  },
  confidenceFill: {
    height: '100%',
    borderRadius: '3px',
    background: 'var(--accent)',
    transition: 'width 0.3s ease',
  },
};

export default MonsterCard;
