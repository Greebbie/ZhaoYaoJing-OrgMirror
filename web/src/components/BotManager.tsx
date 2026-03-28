import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { API_BASE } from '../services/api';

type Platform = 'feishu' | 'wecom' | 'slack';
type BotStatus = 'active' | 'inactive' | 'error';

interface BotConnection {
  id: string;
  platform: Platform;
  status: BotStatus;
  webhook_url: string;
  last_active_at: string | null;
  credentials_keys: string[];
}

interface TestResult {
  status: string;
  message: string;
}

interface PlatformField {
  key: string;
  label: string;
}

const PLATFORM_CONFIG: Record<Platform, { name_zh: string; name_en: string; icon: string; fields: PlatformField[] }> = {
  feishu: {
    name_zh: '飞书',
    name_en: 'Feishu',
    icon: '🪶',
    fields: [
      { key: 'app_id', label: 'App ID' },
      { key: 'app_secret', label: 'App Secret' },
      { key: 'verification_token', label: 'Verification Token' },
      { key: 'encrypt_key', label: 'Encrypt Key' },
    ],
  },
  wecom: {
    name_zh: '企业微信',
    name_en: 'WeCom',
    icon: '💼',
    fields: [
      { key: 'corp_id', label: 'Corp ID' },
      { key: 'agent_id', label: 'Agent ID' },
      { key: 'secret', label: 'Secret' },
      { key: 'token', label: 'Token' },
      { key: 'encoding_aes_key', label: 'Encoding AES Key' },
    ],
  },
  slack: {
    name_zh: 'Slack',
    name_en: 'Slack',
    icon: '💬',
    fields: [
      { key: 'bot_token', label: 'Bot Token' },
      { key: 'signing_secret', label: 'Signing Secret' },
      { key: 'app_token', label: 'App Token' },
    ],
  },
};

const WEBHOOK_PATHS: Record<Platform, string> = {
  feishu: '/api/bot/feishu/webhook',
  wecom: '/api/bot/wecom/webhook',
  slack: '/api/bot/slack/events',
};

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unexpected error';
}

function BotManager() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const [bots, setBots] = useState<BotConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [configuringPlatform, setConfiguringPlatform] = useState<Platform | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<Record<string, TestResult>>({});
  const [copiedPlatform, setCopiedPlatform] = useState<Platform | null>(null);

  const fetchBots = useCallback(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/admin/bots`);
      if (!resp.ok) throw new Error(`${resp.status}`);
      const data = await resp.json();
      setBots(data.bots ?? []);
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBots();
  }, [fetchBots]);

  function getBotForPlatform(platform: Platform): BotConnection | undefined {
    return bots.find((b) => b.platform === platform);
  }

  function getStatusBadge(bot: BotConnection | undefined): { label: string; color: string; bg: string } {
    if (!bot || bot.status === 'inactive') {
      return {
        label: t('not_configured'),
        color: '#6b7280',
        bg: '#f3f4f6',
      };
    }
    if (bot.status === 'active') {
      return {
        label: t('connected'),
        color: '#15803d',
        bg: '#dcfce7',
      };
    }
    return {
      label: t('error'),
      color: '#dc2626',
      bg: '#fee2e2',
    };
  }

  function handleConfigure(platform: Platform) {
    const initialValues: Record<string, string> = {};
    for (const field of PLATFORM_CONFIG[platform].fields) {
      initialValues[field.key] = '';
    }
    setFormValues(initialValues);
    setConfiguringPlatform(platform);
  }

  function handleFormChange(key: string, value: string) {
    setFormValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSave() {
    if (!configuringPlatform) return;
    setSaving(true);
    try {
      const resp = await fetch(`${API_BASE}/api/admin/bots`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: configuringPlatform,
          credentials: formValues,
        }),
      });
      if (!resp.ok) throw new Error(`Save failed: ${resp.status}`);
      await fetchBots();
      // Keep form open to show webhook URL
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function handleTest(botId: string) {
    setTestingId(botId);
    try {
      const resp = await fetch(`${API_BASE}/api/admin/bots/${botId}/test`, {
        method: 'POST',
      });
      if (!resp.ok) throw new Error(`Test failed: ${resp.status}`);
      const result: TestResult = await resp.json();
      setTestResult((prev) => ({ ...prev, [botId]: result }));
    } catch (e: unknown) {
      setTestResult((prev) => ({
        ...prev,
        [botId]: { status: 'error', message: getErrorMessage(e) },
      }));
    } finally {
      setTestingId(null);
    }
  }

  async function handleDelete(botId: string) {
    try {
      const resp = await fetch(`${API_BASE}/api/admin/bots/${botId}`, {
        method: 'DELETE',
      });
      if (!resp.ok) throw new Error(`Delete failed: ${resp.status}`);
      await fetchBots();
      setConfiguringPlatform(null);
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    }
  }

  function handleCopyWebhook(platform: Platform) {
    const url = `${window.location.origin}${WEBHOOK_PATHS[platform]}`;
    navigator.clipboard.writeText(url).then(() => {
      setCopiedPlatform(platform);
      setTimeout(() => setCopiedPlatform(null), 2000);
    });
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 40, color: 'var(--text)' }}>{lang === 'zh' ? '加载中...' : 'Loading...'}</div>;
  }

  if (error) {
    return <div style={{ color: '#ef4444', padding: 20 }}>Error: {error}</div>;
  }

  const platforms: Platform[] = ['feishu', 'wecom', 'slack'];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {platforms.map((platform) => {
        const config = PLATFORM_CONFIG[platform];
        const bot = getBotForPlatform(platform);
        const badge = getStatusBadge(bot);
        const isConfiguring = configuringPlatform === platform;
        const platformTestResult = bot ? testResult[bot.id] : undefined;

        return (
          <div key={platform} style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: isConfiguring ? 16 : 0 }}>
              <span style={{ fontSize: 28 }}>{config.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, color: 'var(--text-h)', fontSize: 16 }}>
                  {lang === 'zh' ? config.name_zh : config.name_en}
                </div>
                {bot?.last_active_at && (
                  <div style={{ fontSize: 12, color: 'var(--text)', marginTop: 2 }}>
                    {t('last_active')}: {new Date(bot.last_active_at).toLocaleString()}
                  </div>
                )}
              </div>
              <span
                style={{
                  padding: '3px 10px',
                  borderRadius: 12,
                  fontSize: 12,
                  fontWeight: 600,
                  color: badge.color,
                  background: badge.bg,
                }}
              >
                {badge.label}
              </span>
              <div style={{ display: 'flex', gap: 8 }}>
                <button style={btnStyle} onClick={() => isConfiguring ? setConfiguringPlatform(null) : handleConfigure(platform)}>
                  {isConfiguring ? t('cancel') : t('configure')}
                </button>
                {bot && (
                  <button
                    style={{ ...btnStyle, ...btnPrimaryStyle }}
                    onClick={() => handleTest(bot.id)}
                    disabled={testingId === bot.id}
                  >
                    {testingId === bot.id
                      ? (lang === 'zh' ? '测试中...' : 'Testing...')
                      : t('test_connection')}
                  </button>
                )}
              </div>
            </div>

            {/* Test result */}
            {bot && platformTestResult && (
              <div
                style={{
                  marginTop: 8,
                  padding: '8px 12px',
                  borderRadius: 8,
                  fontSize: 13,
                  background: platformTestResult.status === 'ok' ? '#dcfce7' : '#fee2e2',
                  color: platformTestResult.status === 'ok' ? '#15803d' : '#dc2626',
                }}
              >
                {platformTestResult.message}
              </div>
            )}

            {/* Config form */}
            {isConfiguring && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12, borderTop: '1px solid var(--border)', paddingTop: 16 }}>
                {config.fields.map((field) => (
                  <div key={field.key}>
                    <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: 'var(--text-h)', marginBottom: 4 }}>
                      {field.label}
                    </label>
                    <input
                      type={field.key.includes('secret') || field.key.includes('token') || field.key.includes('key') ? 'password' : 'text'}
                      value={formValues[field.key] ?? ''}
                      onChange={(e) => handleFormChange(field.key, e.target.value)}
                      style={inputStyle}
                      placeholder={field.label}
                    />
                  </div>
                ))}

                <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
                  <button
                    style={{ ...btnStyle, ...btnPrimaryStyle }}
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? (lang === 'zh' ? '保存中...' : 'Saving...') : t('save')}
                  </button>
                  <button style={btnStyle} onClick={() => setConfiguringPlatform(null)}>
                    {t('cancel')}
                  </button>
                  {bot && (
                    <button
                      style={{ ...btnStyle, color: '#dc2626', borderColor: '#fca5a5' }}
                      onClick={() => handleDelete(bot.id)}
                    >
                      {t('delete')}
                    </button>
                  )}
                </div>

                {/* Webhook URL */}
                {bot && bot.status !== 'inactive' && (
                  <div style={{ marginTop: 8, padding: '10px 14px', background: 'var(--code-bg)', borderRadius: 8 }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-h)', marginBottom: 4 }}>
                      {t('webhook_url')}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <code style={{ flex: 1, fontSize: 13, wordBreak: 'break-all' }}>
                        {window.location.origin}{WEBHOOK_PATHS[platform]}
                      </code>
                      <button
                        style={{ ...btnStyle, fontSize: 12, padding: '4px 10px' }}
                        onClick={() => handleCopyWebhook(platform)}
                      >
                        {copiedPlatform === platform
                          ? (lang === 'zh' ? '已复制' : 'Copied')
                          : (lang === 'zh' ? '复制' : 'Copy')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: 12,
  padding: 20,
};

const btnStyle: React.CSSProperties = {
  padding: '6px 14px',
  borderRadius: 6,
  border: '1px solid var(--border)',
  background: 'var(--bg)',
  color: 'var(--text-h)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
  fontFamily: 'var(--sans)',
  transition: 'border-color 0.15s',
};

const btnPrimaryStyle: React.CSSProperties = {
  background: 'var(--accent)',
  color: '#fff',
  borderColor: 'var(--accent)',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 12px',
  borderRadius: 6,
  border: '1px solid var(--border)',
  background: 'var(--bg)',
  color: 'var(--text-h)',
  fontSize: 14,
  fontFamily: 'var(--sans)',
  boxSizing: 'border-box',
};

export default BotManager;
