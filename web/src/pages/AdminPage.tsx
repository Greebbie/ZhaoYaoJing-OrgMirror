import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import BotManager from '../components/BotManager';
import TeamManager from '../components/TeamManager';

type Tab = 'bots' | 'team';

function AdminPage() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<Tab>('bots');

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <h1 style={styles.title}>{t('admin')}</h1>
      </div>

      <div style={styles.tabs}>
        <button
          style={{
            ...styles.tab,
            ...(activeTab === 'bots' ? styles.tabActive : {}),
          }}
          onClick={() => setActiveTab('bots')}
        >
          {t('bots')}
        </button>
        <button
          style={{
            ...styles.tab,
            ...(activeTab === 'team' ? styles.tabActive : {}),
          }}
          onClick={() => setActiveTab('team')}
        >
          {t('team')}
        </button>
      </div>

      {activeTab === 'bots' && <BotManager />}
      {activeTab === 'team' && <TeamManager />}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    padding: '24px 32px 48px',
    maxWidth: '960px',
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
  tabs: {
    display: 'flex',
    gap: '4px',
    borderBottom: '1px solid var(--border)',
    paddingBottom: '0',
  },
  tab: {
    padding: '10px 24px',
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--text)',
    background: 'none',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    transition: 'color 0.15s, border-color 0.15s',
    fontFamily: 'var(--sans)',
  },
  tabActive: {
    color: 'var(--accent)',
    fontWeight: 600,
    borderBottomColor: 'var(--accent)',
  },
};

export default AdminPage;
