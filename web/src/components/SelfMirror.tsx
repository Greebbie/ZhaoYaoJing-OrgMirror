import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { analyzeSelfMirror } from '../services/api';
import type { SelfMirrorResult } from '../services/api';

type ActionChoice = 'original' | 'suggestion' | 'edit';

const SEVERITY_COLORS: Record<number, string> = {
  1: '#16a34a',
  2: '#ca8a04',
  3: '#dc2626',
  4: '#6b21a8',
};

function SelfMirror() {
  const { t, i18n } = useTranslation();
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<SelfMirrorResult | null>(null);
  const [chosenAction, setChosenAction] = useState<ActionChoice | null>(null);
  const [editedText, setEditedText] = useState('');

  const language = i18n.language === 'en' ? 'en' : 'zh';

  const handleCheck = async () => {
    if (!draft.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setChosenAction(null);

    try {
      const res = await analyzeSelfMirror(draft.trim(), language);
      setResult(res);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = (action: ActionChoice) => {
    setChosenAction(action);
    if (action === 'edit') {
      setEditedText(draft);
    }
  };

  const finalText = chosenAction === 'suggestion' && result
    ? result.suggested_rewrite
    : chosenAction === 'edit'
      ? editedText
      : draft;

  return (
    <div style={styles.container}>
      <div style={styles.inputSection}>
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t('self_mirror_placeholder')}
          style={styles.textarea}
          rows={6}
          disabled={loading}
        />
        <button
          onClick={handleCheck}
          disabled={loading || !draft.trim()}
          style={{
            ...styles.checkButton,
            opacity: loading || !draft.trim() ? 0.5 : 1,
          }}
        >
          {loading ? t('analyzing') : t('check_my_message')}
        </button>
      </div>

      {error && (
        <div style={styles.error}>{error}</div>
      )}

      {result && (
        <div style={styles.resultSection}>
          {/* Detected patterns */}
          {result.patterns_detected.length > 0 && (
            <div style={styles.patternsSection}>
              <h3 style={styles.subTitle}>{t('patterns_detected')}</h3>
              <div style={styles.patternsList}>
                {result.patterns_detected.map((p, i) => (
                  <div key={i} style={styles.patternItem}>
                    <span
                      style={{
                        ...styles.patternDot,
                        background: SEVERITY_COLORS[p.severity] ?? '#ca8a04',
                      }}
                    />
                    <div>
                      <span style={styles.patternName}>{p.pattern}</span>
                      <span style={styles.patternDesc}>
                        {language === 'zh' ? p.description_zh : p.description_en}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Suggested rewrite */}
          <div style={styles.rewriteSection}>
            <h3 style={styles.subTitle}>{t('suggested_rewrite')}</h3>
            <div style={styles.rewriteBox}>{result.suggested_rewrite}</div>
          </div>

          {/* Comparison */}
          {result.comparison && (
            <div style={styles.comparisonSection}>
              <div style={styles.comparisonScores}>
                <div style={styles.scoreBox}>
                  <span style={styles.scoreLabel}>{t('original_score')}</span>
                  <span style={styles.scoreValue}>{result.comparison.original_score}</span>
                </div>
                <span style={styles.arrow}>→</span>
                <div style={styles.scoreBox}>
                  <span style={styles.scoreLabel}>{t('rewrite_score')}</span>
                  <span style={{ ...styles.scoreValue, color: '#16a34a' }}>
                    {result.comparison.rewrite_score}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Action buttons */}
          {!chosenAction && (
            <div style={styles.actions}>
              <button
                onClick={() => handleAction('original')}
                style={styles.actionButton}
              >
                {t('send_original')}
              </button>
              <button
                onClick={() => handleAction('suggestion')}
                style={{ ...styles.actionButton, ...styles.primaryAction }}
              >
                {t('use_suggestion')}
              </button>
              <button
                onClick={() => handleAction('edit')}
                style={styles.actionButton}
              >
                {t('edit_myself')}
              </button>
            </div>
          )}

          {/* Edit mode */}
          {chosenAction === 'edit' && (
            <div style={styles.editSection}>
              <textarea
                value={editedText}
                onChange={(e) => setEditedText(e.target.value)}
                style={styles.textarea}
                rows={4}
              />
            </div>
          )}

          {/* Final text display */}
          {chosenAction && (
            <div style={styles.finalSection}>
              <h3 style={styles.subTitle}>{t('final_message')}</h3>
              <div style={styles.finalBox}>{finalText}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    width: '100%',
    textAlign: 'left',
  },
  inputSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
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
  checkButton: {
    alignSelf: 'flex-start',
    padding: '10px 24px',
    borderRadius: '8px',
    border: 'none',
    background: 'var(--accent)',
    color: '#fff',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'opacity 0.2s',
  },
  error: {
    padding: '12px 16px',
    borderRadius: '8px',
    background: '#fee2e2',
    color: '#991b1b',
    fontSize: '14px',
  },
  resultSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
    borderTop: '1px solid var(--border)',
    paddingTop: '20px',
  },
  subTitle: {
    fontSize: '16px',
    fontWeight: 600,
    color: 'var(--text-h)',
    margin: '0 0 8px',
  },
  patternsSection: {},
  patternsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  patternItem: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '10px',
    padding: '10px 14px',
    borderRadius: '6px',
    background: 'var(--code-bg)',
  },
  patternDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    marginTop: '6px',
    flexShrink: 0,
  },
  patternName: {
    fontSize: '14px',
    fontWeight: 600,
    color: 'var(--text-h)',
    display: 'block',
  },
  patternDesc: {
    fontSize: '13px',
    color: 'var(--text)',
  },
  rewriteSection: {},
  rewriteBox: {
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--code-bg)',
    fontSize: '15px',
    lineHeight: '1.6',
    color: 'var(--text-h)',
    whiteSpace: 'pre-wrap',
  },
  comparisonSection: {},
  comparisonScores: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    justifyContent: 'center',
  },
  scoreBox: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '12px 24px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
  },
  scoreLabel: {
    fontSize: '12px',
    color: 'var(--text)',
    marginBottom: '4px',
  },
  scoreValue: {
    fontSize: '28px',
    fontWeight: 700,
    color: 'var(--text-h)',
  },
  arrow: {
    fontSize: '24px',
    color: 'var(--text)',
  },
  actions: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
  },
  actionButton: {
    padding: '10px 20px',
    borderRadius: '8px',
    border: '1px solid var(--border)',
    background: 'var(--bg)',
    color: 'var(--text-h)',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  primaryAction: {
    background: 'var(--accent)',
    color: '#fff',
    border: 'none',
  },
  editSection: {
    marginTop: '8px',
  },
  finalSection: {
    borderTop: '1px solid var(--border)',
    paddingTop: '16px',
  },
  finalBox: {
    padding: '16px',
    borderRadius: '8px',
    border: '2px solid var(--accent)',
    background: 'var(--accent-bg)',
    fontSize: '15px',
    lineHeight: '1.6',
    color: 'var(--text-h)',
    whiteSpace: 'pre-wrap',
  },
};

export default SelfMirror;
