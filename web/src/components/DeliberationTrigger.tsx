import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { API_BASE } from '../services/api';

interface Props {
  content: string;
  onResult: (result: any) => void;
}

export default function DeliberationTrigger({ content, onResult }: Props) {
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const [parties, setParties] = useState<string[]>(['', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addParty = () => {
    if (parties.length < 5) setParties([...parties, '']);
  };

  const removeParty = (index: number) => {
    if (parties.length > 2) setParties(parties.filter((_, i) => i !== index));
  };

  const updateParty = (index: number, value: string) => {
    const updated = [...parties];
    updated[index] = value;
    setParties(updated);
  };

  const handleSubmit = async () => {
    const validParties = parties.filter(p => p.trim());
    if (validParties.length < 2) {
      setError(lang === 'zh' ? '至少需要 2 个利益方' : 'Need at least 2 parties');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const resp = await fetch(`${API_BASE}/api/deliberate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, parties: validParties }),
      });
      if (!resp.ok) throw new Error(`Error: ${resp.status}`);
      const data = await resp.json();
      onResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #d1d5db', borderRadius: 8, padding: 16, marginTop: 16, background: '#f9fafb' }}>
      <h4 style={{ marginTop: 0 }}>
        {lang === 'zh' ? '⚖️ 发起审议' : '⚖️ Start Deliberation'}
      </h4>
      <p style={{ fontSize: 13, color: '#6b7280', marginTop: 0 }}>
        {lang === 'zh'
          ? '定义讨论中的各利益方，照妖镜将模拟多方审议并生成方案'
          : 'Define the stakeholder parties. ZhaoYaoJing will simulate multi-party deliberation.'}
      </p>

      {parties.map((party, i) => (
        <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'center' }}>
          <span style={{ minWidth: 60, fontSize: 13, color: '#6b7280' }}>
            {lang === 'zh' ? `利益方 ${i + 1}` : `Party ${i + 1}`}
          </span>
          <input
            type="text"
            value={party}
            onChange={e => updateParty(i, e.target.value)}
            placeholder={lang === 'zh' ? '例：产品经理（推动方）' : 'e.g. Product Manager (initiator)'}
            style={{ flex: 1, padding: '6px 10px', border: '1px solid #d1d5db', borderRadius: 6, fontSize: 14 }}
          />
          {parties.length > 2 && (
            <button onClick={() => removeParty(i)} style={{ padding: '4px 8px', border: 'none', cursor: 'pointer', color: '#ef4444' }}>
              ✕
            </button>
          )}
        </div>
      ))}

      <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
        {parties.length < 5 && (
          <button onClick={addParty} style={{ padding: '6px 14px', border: '1px dashed #d1d5db', borderRadius: 6, background: 'white', cursor: 'pointer', fontSize: 13 }}>
            + {lang === 'zh' ? '添加利益方' : 'Add Party'}
          </button>
        )}
        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            padding: '6px 20px', borderRadius: 6, border: 'none', cursor: loading ? 'wait' : 'pointer',
            background: '#7c3aed', color: 'white', fontWeight: 600, fontSize: 14,
            opacity: loading ? 0.6 : 1,
          }}
        >
          {loading
            ? (lang === 'zh' ? '审议中...' : 'Deliberating...')
            : (lang === 'zh' ? '开始审议' : 'Start Deliberation')}
        </button>
      </div>

      {error && <div style={{ color: '#ef4444', marginTop: 8, fontSize: 13 }}>{error}</div>}
    </div>
  );
}
