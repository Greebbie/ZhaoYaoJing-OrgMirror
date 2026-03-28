import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface SetupConfig {
  orgType: string;
  channels: string[];
  painPoints: string[];
  llmBackend: string;
  apiKey: string;
}

const EMPTY_CONFIG: SetupConfig = {
  orgType: '',
  channels: [],
  painPoints: [],
  llmBackend: '',
  apiKey: '',
};

const ORG_TYPES = [
  { id: 'startup', emoji: '🚀' },
  { id: 'mid_large', emoji: '🏢' },
  { id: 'research', emoji: '🔬' },
];

const CHANNELS = ['wechat', 'feishu', 'slack', 'dingtalk', 'email'];

const PAIN_POINTS = [
  'requirements_unclear',
  'things_stuck',
  'nobody_owns',
  'verbal_yes_actual_no',
  'meetings_no_outcomes',
  'politics',
];

const LLM_BACKENDS = [
  { id: 'openai', label: 'OpenAI' },
  { id: 'qwen', label: 'Qwen (通义千问)' },
  { id: 'gemini', label: 'Google Gemini' },
  { id: 'minimax', label: 'MiniMax' },
];

const TOTAL_STEPS = 4;

const STORAGE_KEY = 'zhaoyaojing_setup';

function loadSavedConfig(): SetupConfig {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved) as SetupConfig;
    }
  } catch {
    // Ignore parse errors
  }
  return { ...EMPTY_CONFIG };
}

function SetupWizard() {
  const { t } = useTranslation();
  const [step, setStep] = useState(1);
  const [config, setConfig] = useState<SetupConfig>(loadSavedConfig);
  const [saved, setSaved] = useState(false);

  const updateConfig = (partial: Partial<SetupConfig>): void => {
    setConfig((prev) => ({ ...prev, ...partial }));
  };

  const toggleInArray = (arr: string[], item: string): string[] => {
    return arr.includes(item) ? arr.filter((x) => x !== item) : [...arr, item];
  };

  const canProceed = (): boolean => {
    switch (step) {
      case 1: return config.orgType !== '';
      case 2: return config.channels.length > 0;
      case 3: return config.painPoints.length > 0;
      case 4: return config.llmBackend !== '' && config.apiKey.trim() !== '';
      default: return false;
    }
  };

  const handleFinish = () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    setSaved(true);
  };

  if (saved) {
    return (
      <div style={styles.doneContainer}>
        <span style={styles.doneEmoji}>✅</span>
        <h2 style={styles.doneTitle}>{t('setup_complete')}</h2>
        <p style={styles.doneText}>{t('setup_complete_desc')}</p>
        <button
          onClick={() => { setSaved(false); setStep(1); }}
          style={styles.resetButton}
        >
          {t('reconfigure')}
        </button>
      </div>
    );
  }

  return (
    <div style={styles.wizard}>
      {/* Progress indicator */}
      <div style={styles.progress}>
        {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((s) => (
          <div
            key={s}
            style={{
              ...styles.progressDot,
              background: s <= step ? 'var(--accent)' : 'var(--border)',
            }}
          />
        ))}
      </div>
      <div style={styles.stepLabel}>
        {t('step_n_of_total', { n: step, total: TOTAL_STEPS })}
      </div>

      {/* Step 1: Org type */}
      {step === 1 && (
        <div style={styles.stepContent}>
          <h2 style={styles.stepTitle}>{t('setup_org_type')}</h2>
          <div style={styles.cardGrid}>
            {ORG_TYPES.map((org) => (
              <button
                key={org.id}
                onClick={() => updateConfig({ orgType: org.id })}
                style={{
                  ...styles.orgCard,
                  borderColor: config.orgType === org.id ? 'var(--accent)' : 'var(--border)',
                  background: config.orgType === org.id ? 'var(--accent-bg)' : 'var(--bg)',
                }}
              >
                <span style={styles.orgEmoji}>{org.emoji}</span>
                <span style={styles.orgLabel}>{t(`org_type_${org.id}`)}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Step 2: Channels */}
      {step === 2 && (
        <div style={styles.stepContent}>
          <h2 style={styles.stepTitle}>{t('setup_channels')}</h2>
          <div style={styles.checkboxGrid}>
            {CHANNELS.map((ch) => (
              <label key={ch} style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={config.channels.includes(ch)}
                  onChange={() => updateConfig({ channels: toggleInArray(config.channels, ch) })}
                  style={styles.checkbox}
                />
                <span>{t(`channel_${ch}`)}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Pain points */}
      {step === 3 && (
        <div style={styles.stepContent}>
          <h2 style={styles.stepTitle}>{t('setup_pain_points')}</h2>
          <div style={styles.checkboxGrid}>
            {PAIN_POINTS.map((pp) => (
              <label key={pp} style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={config.painPoints.includes(pp)}
                  onChange={() => updateConfig({ painPoints: toggleInArray(config.painPoints, pp) })}
                  style={styles.checkbox}
                />
                <span>{t(`pain_${pp}`)}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Step 4: LLM backend */}
      {step === 4 && (
        <div style={styles.stepContent}>
          <h2 style={styles.stepTitle}>{t('setup_llm')}</h2>
          <div style={styles.cardGrid}>
            {LLM_BACKENDS.map((llm) => (
              <button
                key={llm.id}
                onClick={() => updateConfig({ llmBackend: llm.id })}
                style={{
                  ...styles.llmCard,
                  borderColor: config.llmBackend === llm.id ? 'var(--accent)' : 'var(--border)',
                  background: config.llmBackend === llm.id ? 'var(--accent-bg)' : 'var(--bg)',
                }}
              >
                {llm.label}
              </button>
            ))}
          </div>
          <div style={styles.apiKeySection}>
            <label style={styles.apiKeyLabel}>{t('api_key')}</label>
            <input
              type="password"
              value={config.apiKey}
              onChange={(e) => updateConfig({ apiKey: e.target.value })}
              placeholder={t('api_key_placeholder')}
              style={styles.apiKeyInput}
            />
          </div>
        </div>
      )}

      {/* Navigation */}
      <div style={styles.navigation}>
        {step > 1 && (
          <button
            onClick={() => setStep((s) => s - 1)}
            style={styles.navButton}
          >
            {t('back')}
          </button>
        )}
        <div style={{ flex: 1 }} />
        {step < TOTAL_STEPS ? (
          <button
            onClick={() => setStep((s) => s + 1)}
            disabled={!canProceed()}
            style={{
              ...styles.navButton,
              ...styles.navPrimary,
              opacity: canProceed() ? 1 : 0.5,
            }}
          >
            {t('next')}
          </button>
        ) : (
          <button
            onClick={handleFinish}
            disabled={!canProceed()}
            style={{
              ...styles.navButton,
              ...styles.navPrimary,
              opacity: canProceed() ? 1 : 0.5,
            }}
          >
            {t('start')}
          </button>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  wizard: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    maxWidth: '600px',
    margin: '0 auto',
    textAlign: 'left',
  },
  progress: {
    display: 'flex',
    gap: '8px',
    justifyContent: 'center',
  },
  progressDot: {
    width: '40px',
    height: '4px',
    borderRadius: '2px',
    transition: 'background 0.3s',
  },
  stepLabel: {
    textAlign: 'center',
    fontSize: '13px',
    color: 'var(--text)',
  },
  stepContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  stepTitle: {
    fontSize: '22px',
    fontWeight: 600,
    color: 'var(--text-h)',
    margin: 0,
    textAlign: 'center',
  },
  cardGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
    gap: '12px',
  },
  orgCard: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    padding: '24px 16px',
    borderRadius: '12px',
    border: '2px solid',
    cursor: 'pointer',
    transition: 'border-color 0.2s, background 0.2s',
    fontFamily: 'var(--sans)',
    fontSize: '15px',
  },
  orgEmoji: {
    fontSize: '36px',
  },
  orgLabel: {
    fontWeight: 500,
    color: 'var(--text-h)',
  },
  checkboxGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    cursor: 'pointer',
    fontSize: '15px',
    color: 'var(--text-h)',
    transition: 'background 0.15s',
  },
  checkbox: {
    width: '18px',
    height: '18px',
    cursor: 'pointer',
  },
  llmCard: {
    padding: '16px',
    borderRadius: '10px',
    border: '2px solid',
    cursor: 'pointer',
    transition: 'border-color 0.2s, background 0.2s',
    fontFamily: 'var(--sans)',
    fontSize: '15px',
    fontWeight: 500,
    color: 'var(--text-h)',
    textAlign: 'center',
  },
  apiKeySection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    marginTop: '8px',
  },
  apiKeyLabel: {
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--text-h)',
  },
  apiKeyInput: {
    padding: '10px 14px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontSize: '15px',
    fontFamily: 'var(--mono)',
    outline: 'none',
  },
  navigation: {
    display: 'flex',
    gap: '12px',
    paddingTop: '8px',
    borderTop: '1px solid var(--border)',
  },
  navButton: {
    padding: '10px 24px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontSize: '15px',
    fontWeight: 500,
    cursor: 'pointer',
    fontFamily: 'var(--sans)',
    transition: 'opacity 0.2s',
  },
  navPrimary: {
    background: 'var(--accent)',
    color: '#fff',
    border: 'none',
  },
  doneContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '12px',
    padding: '48px 24px',
  },
  doneEmoji: {
    fontSize: '48px',
  },
  doneTitle: {
    fontSize: '24px',
    fontWeight: 600,
    color: 'var(--text-h)',
    margin: 0,
  },
  doneText: {
    fontSize: '16px',
    color: 'var(--text)',
    margin: 0,
    textAlign: 'center',
  },
  resetButton: {
    marginTop: '12px',
    padding: '8px 20px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontSize: '14px',
    cursor: 'pointer',
    fontFamily: 'var(--sans)',
  },
};

export default SetupWizard;
