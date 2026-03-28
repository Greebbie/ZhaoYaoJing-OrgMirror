import { useTranslation } from 'react-i18next';

interface Party {
  role: string;
  position: string;
  constraints: string[];
}

interface Option {
  label: string;
  description: string;
  trade_offs: string[];
}

interface DeliberationData {
  conflict_type: string;
  parties_summary: Party[];
  options: Option[];
  unresolved: string[];
  recommended_option: string | null;
  escalation_recommendation: string | null;
  meta_warning?: string;
}

interface Props {
  deliberation: DeliberationData;
  advocatePositions: any[];
  roundsCompleted: number;
}

const conflictTypeLabels: Record<string, { zh: string; en: string }> = {
  resource_conflict: { zh: '资源争夺', en: 'Resource Conflict' },
  priority_conflict: { zh: '优先级分歧', en: 'Priority Conflict' },
  scope_conflict: { zh: '范围分歧', en: 'Scope Conflict' },
  authority_conflict: { zh: '权限争议', en: 'Authority Conflict' },
  information_gap: { zh: '信息不对称', en: 'Information Gap' },
};

const positionColors: Record<string, string> = {
  support: '#22c55e',
  oppose: '#ef4444',
  conditional: '#eab308',
};

export default function DeliberationPanel({ deliberation, advocatePositions: _advocatePositions, roundsCompleted }: Props) {
  void _advocatePositions; // Reserved for future detailed position display
  const { i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const conflictLabel = conflictTypeLabels[deliberation.conflict_type]?.[lang] || deliberation.conflict_type;

  return (
    <div style={{ border: '2px solid #7c3aed', borderRadius: 12, padding: 20, marginTop: 20, background: '#faf5ff' }}>
      <h3 style={{ color: '#7c3aed', marginTop: 0 }}>
        {lang === 'zh' ? '⚖️ 审议结果' : '⚖️ Deliberation Result'}
      </h3>

      {deliberation.meta_warning && (
        <div style={{ background: '#fef3c7', padding: 12, borderRadius: 8, marginBottom: 16, border: '1px solid #f59e0b' }}>
          {deliberation.meta_warning}
        </div>
      )}

      <div style={{ marginBottom: 16 }}>
        <strong>{lang === 'zh' ? '冲突类型：' : 'Conflict Type: '}</strong>
        <span style={{ background: '#e9d5ff', padding: '2px 8px', borderRadius: 4 }}>{conflictLabel}</span>
        <span style={{ marginLeft: 12, color: '#6b7280', fontSize: 13 }}>
          {lang === 'zh' ? `完成 ${roundsCompleted} 轮审议` : `${roundsCompleted} rounds completed`}
        </span>
      </div>

      {/* Parties */}
      <div style={{ marginBottom: 16 }}>
        <h4 style={{ marginBottom: 8 }}>{lang === 'zh' ? '各方立场' : 'Party Positions'}</h4>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {deliberation.parties_summary.map((p, i) => (
            <div key={i} style={{ flex: '1 1 200px', padding: 12, background: 'white', borderRadius: 8, borderLeft: `4px solid ${positionColors[p.position] || '#9ca3af'}` }}>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>{p.role}</div>
              <div style={{ fontSize: 13, color: positionColors[p.position], fontWeight: 500, marginBottom: 4 }}>
                {p.position === 'support' ? (lang === 'zh' ? '支持' : 'Support') :
                 p.position === 'oppose' ? (lang === 'zh' ? '反对' : 'Oppose') :
                 (lang === 'zh' ? '有条件支持' : 'Conditional')}
              </div>
              {p.constraints.length > 0 && (
                <div style={{ fontSize: 12, color: '#6b7280' }}>
                  {p.constraints.join('; ')}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Options */}
      <div style={{ marginBottom: 16 }}>
        <h4 style={{ marginBottom: 8 }}>{lang === 'zh' ? '方案选项' : 'Options'}</h4>
        {deliberation.options.map((opt, i) => (
          <div key={i} style={{
            padding: 12, background: 'white', borderRadius: 8, marginBottom: 8,
            border: opt.label === deliberation.recommended_option ? '2px solid #7c3aed' : '1px solid #e5e7eb',
          }}>
            <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
              {opt.label}
              {opt.label === deliberation.recommended_option && (
                <span style={{ fontSize: 11, background: '#7c3aed', color: 'white', padding: '1px 6px', borderRadius: 4 }}>
                  {lang === 'zh' ? '推荐' : 'Recommended'}
                </span>
              )}
            </div>
            <div style={{ marginTop: 4, fontSize: 14 }}>{opt.description}</div>
            {opt.trade_offs.length > 0 && (
              <div style={{ marginTop: 4, fontSize: 12, color: '#6b7280' }}>
                {lang === 'zh' ? '取舍：' : 'Trade-offs: '}{opt.trade_offs.join(' | ')}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Unresolved */}
      {deliberation.unresolved.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <h4 style={{ marginBottom: 8, color: '#dc2626' }}>
            {lang === 'zh' ? '⚠️ 未解决项' : '⚠️ Unresolved'}
          </h4>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {deliberation.unresolved.map((item, i) => (
              <li key={i} style={{ fontSize: 14 }}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {deliberation.escalation_recommendation && (
        <div style={{ background: '#fee2e2', padding: 12, borderRadius: 8, fontSize: 14 }}>
          <strong>{lang === 'zh' ? '升级建议：' : 'Escalation: '}</strong>
          {deliberation.escalation_recommendation}
        </div>
      )}
    </div>
  );
}
