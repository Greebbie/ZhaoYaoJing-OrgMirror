import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { MirrorInput as MirrorInputType } from '../services/api';

interface MirrorInputProps {
  onSubmit: (input: MirrorInputType) => void;
  loading: boolean;
}

const CONTENT_TYPES = [
  'chat_log',
  'meeting_notes',
  'email_thread',
  'requirement_doc',
  'free_text',
] as const;

const LANGUAGES = ['auto', 'zh', 'en'] as const;

function MirrorInput({ onSubmit, loading }: MirrorInputProps) {
  const { t } = useTranslation();
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState<MirrorInputType['content_type']>('chat_log');
  const [language, setLanguage] = useState<MirrorInputType['language']>('auto');
  const [anonymousMode, setAnonymousMode] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit({
      content: content.trim(),
      content_type: contentType,
      language,
      trigger_mode: 'manual',
      anonymous_mode: anonymousMode,
    });
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={t('mirror_input_placeholder')}
        style={styles.textarea}
        rows={8}
        disabled={loading}
      />

      <div style={styles.controls}>
        <div style={styles.controlGroup}>
          <label style={styles.label}>{t('content_type')}</label>
          <select
            value={contentType}
            onChange={(e) => setContentType(e.target.value as MirrorInputType['content_type'])}
            style={styles.select}
            disabled={loading}
          >
            {CONTENT_TYPES.map((ct) => (
              <option key={ct} value={ct}>
                {t(`content_type_${ct}`)}
              </option>
            ))}
          </select>
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.label}>{t('language')}</label>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as MirrorInputType['language'])}
            style={styles.select}
            disabled={loading}
          >
            {LANGUAGES.map((lang) => (
              <option key={lang} value={lang}>
                {t(`lang_${lang}`)}
              </option>
            ))}
          </select>
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.toggleLabel}>
            <input
              type="checkbox"
              checked={anonymousMode}
              onChange={(e) => setAnonymousMode(e.target.checked)}
              disabled={loading}
              style={styles.checkbox}
            />
            <span>{t('anonymous_mode')}</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={loading || !content.trim()}
          style={{
            ...styles.button,
            opacity: loading || !content.trim() ? 0.5 : 1,
          }}
        >
          {loading ? t('analyzing') : t('analyze')}
        </button>
      </div>
    </form>
  );
}

const styles: Record<string, React.CSSProperties> = {
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
    width: '100%',
  },
  textarea: {
    width: '100%',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontFamily: 'var(--sans)',
    fontSize: '16px',
    lineHeight: '1.6',
    resize: 'vertical',
    boxSizing: 'border-box',
    outline: 'none',
  },
  controls: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '16px',
    alignItems: 'flex-end',
  },
  controlGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  label: {
    fontSize: '13px',
    color: 'var(--text)',
    fontWeight: 500,
  },
  select: {
    padding: '8px 12px',
    borderRadius: '6px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontSize: '14px',
    cursor: 'pointer',
  },
  toggleLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '14px',
    color: 'var(--text-h)',
    cursor: 'pointer',
    padding: '8px 0',
  },
  checkbox: {
    width: '16px',
    height: '16px',
    cursor: 'pointer',
  },
  button: {
    padding: '10px 28px',
    borderRadius: '8px',
    border: 'none',
    background: 'var(--accent)',
    color: '#fff',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    marginLeft: 'auto',
    transition: 'opacity 0.2s',
  },
};

export default MirrorInput;
