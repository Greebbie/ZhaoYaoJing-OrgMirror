import { useTranslation } from 'react-i18next';
import SetupWizard from '../components/SetupWizard';

function SetupPage() {
  const { t } = useTranslation();

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>{t('setup')}</h1>
        <p style={styles.description}>{t('setup_desc')}</p>
      </div>

      <SetupWizard />
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    gap: '28px',
    padding: '24px 32px 48px',
    maxWidth: '760px',
    margin: '0 auto',
    width: '100%',
    boxSizing: 'border-box',
  },
  header: {
    textAlign: 'center',
  },
  title: {
    fontSize: '36px',
    fontWeight: 700,
    color: 'var(--text-h)',
    margin: '0 0 8px',
    letterSpacing: '-0.5px',
  },
  description: {
    fontSize: '16px',
    color: 'var(--text)',
    margin: 0,
  },
};

export default SetupPage;
