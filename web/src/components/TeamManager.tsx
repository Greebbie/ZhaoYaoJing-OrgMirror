import { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { API_BASE } from '../services/api';

interface Member {
  id: string;
  display_name: string;
  role: string;
  department: string;
  authority_level: number;
}

interface MonsterPattern {
  monster_id: string;
  emoji: string;
  name_zh: string;
  name_en: string;
  count: number;
}

interface MemberFormData {
  display_name: string;
  role: string;
  department: string;
  authority_level: number;
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unexpected error';
}

const EMPTY_FORM: MemberFormData = {
  display_name: '',
  role: '',
  department: '',
  authority_level: 1,
};

function TeamManager() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language === 'en' ? 'en' : 'zh';

  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [formData, setFormData] = useState<MemberFormData>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [selectedMemberId, setSelectedMemberId] = useState<string | null>(null);
  const [patterns, setPatterns] = useState<MonsterPattern[]>([]);
  const [patternsLoading, setPatternsLoading] = useState(false);

  const fetchMembers = useCallback(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/members`);
      if (!resp.ok) throw new Error(`${resp.status}`);
      const data = await resp.json();
      setMembers(data.members ?? []);
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  async function fetchPatterns(memberId: string) {
    setPatternsLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/members/${memberId}/patterns`);
      if (!resp.ok) throw new Error(`${resp.status}`);
      const data = await resp.json();
      setPatterns(data.patterns ?? []);
    } catch (e: unknown) {
      setError(getErrorMessage(e));
      setPatterns([]);
    } finally {
      setPatternsLoading(false);
    }
  }

  function handleSelectMember(memberId: string) {
    if (selectedMemberId === memberId) {
      setSelectedMemberId(null);
      setPatterns([]);
      return;
    }
    setSelectedMemberId(memberId);
    fetchPatterns(memberId);
  }

  function handleAdd() {
    setFormData(EMPTY_FORM);
    setEditingId(null);
    setShowForm(true);
  }

  function handleEdit(member: Member) {
    setFormData({
      display_name: member.display_name,
      role: member.role,
      department: member.department,
      authority_level: member.authority_level,
    });
    setEditingId(member.id);
    setShowForm(true);
  }

  function handleFormChange(key: keyof MemberFormData, value: string | number) {
    setFormData((prev) => ({ ...prev, [key]: value }));
  }

  function handleCancel() {
    setShowForm(false);
    setEditingId(null);
    setFormData(EMPTY_FORM);
  }

  async function handleSave() {
    setSaving(true);
    try {
      if (editingId) {
        const resp = await fetch(`${API_BASE}/api/members/${editingId}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
        if (!resp.ok) throw new Error(`Update failed: ${resp.status}`);
      } else {
        const resp = await fetch(`${API_BASE}/api/members`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        });
        if (!resp.ok) throw new Error(`Create failed: ${resp.status}`);
      }
      await fetchMembers();
      handleCancel();
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(memberId: string) {
    try {
      const resp = await fetch(`${API_BASE}/api/members/${memberId}`, {
        method: 'DELETE',
      });
      if (!resp.ok) throw new Error(`Delete failed: ${resp.status}`);
      if (selectedMemberId === memberId) {
        setSelectedMemberId(null);
        setPatterns([]);
      }
      await fetchMembers();
    } catch (e: unknown) {
      setError(getErrorMessage(e));
    }
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 40, color: 'var(--text)' }}>{lang === 'zh' ? '加载中...' : 'Loading...'}</div>;
  }

  if (error) {
    return <div style={{ color: '#ef4444', padding: 20 }}>Error: {error}</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header with add button */}
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button style={{ ...btnStyle, ...btnPrimaryStyle }} onClick={handleAdd}>
          {t('add_member')}
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 12px', color: 'var(--text-h)' }}>
            {editingId
              ? (lang === 'zh' ? '编辑成员' : 'Edit Member')
              : t('add_member')}
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={labelStyle}>{t('display_name')}</label>
              <input
                style={inputStyle}
                value={formData.display_name}
                onChange={(e) => handleFormChange('display_name', e.target.value)}
                placeholder={t('display_name')}
              />
            </div>
            <div>
              <label style={labelStyle}>{t('role')}</label>
              <input
                style={inputStyle}
                value={formData.role}
                onChange={(e) => handleFormChange('role', e.target.value)}
                placeholder={t('role')}
              />
            </div>
            <div>
              <label style={labelStyle}>{t('department')}</label>
              <input
                style={inputStyle}
                value={formData.department}
                onChange={(e) => handleFormChange('department', e.target.value)}
                placeholder={t('department')}
              />
            </div>
            <div>
              <label style={labelStyle}>{t('authority_level')}</label>
              <input
                type="number"
                min={1}
                max={10}
                style={inputStyle}
                value={formData.authority_level}
                onChange={(e) => handleFormChange('authority_level', parseInt(e.target.value, 10) || 1)}
                placeholder={t('authority_level')}
              />
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            <button
              style={{ ...btnStyle, ...btnPrimaryStyle }}
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? (lang === 'zh' ? '保存中...' : 'Saving...') : t('save')}
            </button>
            <button style={btnStyle} onClick={handleCancel}>
              {t('cancel')}
            </button>
          </div>
        </div>
      )}

      {/* Members table */}
      {members.length === 0 ? (
        <div style={{ ...cardStyle, textAlign: 'center', color: 'var(--text)', padding: 40 }}>
          {lang === 'zh' ? '暂无成员' : 'No members yet'}
        </div>
      ) : (
        <div style={cardStyle}>
          {/* Table header */}
          <div style={{ ...rowStyle, fontWeight: 600, color: 'var(--text-h)', fontSize: 13, borderBottom: '2px solid var(--border)' }}>
            <span style={{ flex: 2 }}>{t('display_name')}</span>
            <span style={{ flex: 1 }}>{t('role')}</span>
            <span style={{ flex: 1 }}>{t('department')}</span>
            <span style={{ flex: 1, textAlign: 'center' }}>{t('authority_level')}</span>
            <span style={{ width: 120, textAlign: 'right' }}></span>
          </div>

          {/* Table rows */}
          {members.map((member, i) => (
            <div key={member.id}>
              <div
                style={{
                  ...rowStyle,
                  borderBottom: i < members.length - 1 ? '1px solid var(--border)' : 'none',
                  background: selectedMemberId === member.id ? 'var(--accent-bg)' : 'transparent',
                }}
              >
                <span
                  style={{
                    flex: 2,
                    fontWeight: 500,
                    color: 'var(--accent)',
                    cursor: 'pointer',
                  }}
                  onClick={() => handleSelectMember(member.id)}
                >
                  {member.display_name}
                </span>
                <span style={{ flex: 1, color: 'var(--text)', fontSize: 14 }}>{member.role}</span>
                <span style={{ flex: 1, color: 'var(--text)', fontSize: 14 }}>{member.department}</span>
                <span style={{ flex: 1, textAlign: 'center', color: 'var(--text)', fontSize: 14 }}>
                  {member.authority_level}
                </span>
                <span style={{ width: 120, display: 'flex', gap: 6, justifyContent: 'flex-end' }}>
                  <button
                    style={{ ...btnSmallStyle }}
                    onClick={() => handleEdit(member)}
                  >
                    {t('edit')}
                  </button>
                  <button
                    style={{ ...btnSmallStyle, color: '#dc2626' }}
                    onClick={() => handleDelete(member.id)}
                  >
                    {t('delete')}
                  </button>
                </span>
              </div>

              {/* Patterns panel */}
              {selectedMemberId === member.id && (
                <div style={{ padding: '12px 16px', background: 'var(--code-bg)', borderRadius: '0 0 8px 8px' }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-h)', marginBottom: 8 }}>
                    {t('patterns')}
                  </div>
                  {patternsLoading ? (
                    <div style={{ fontSize: 13, color: 'var(--text)' }}>
                      {lang === 'zh' ? '加载中...' : 'Loading...'}
                    </div>
                  ) : patterns.length === 0 ? (
                    <div style={{ fontSize: 13, color: 'var(--text)' }}>
                      {lang === 'zh' ? '暂无检测到的妖怪模式' : 'No monster patterns detected'}
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                      {patterns.map((p) => (
                        <span
                          key={p.monster_id}
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: 4,
                            padding: '4px 10px',
                            borderRadius: 16,
                            fontSize: 13,
                            background: 'var(--accent-bg)',
                            color: 'var(--text-h)',
                            fontWeight: 500,
                          }}
                        >
                          {p.emoji} {lang === 'zh' ? p.name_zh : p.name_en} x {p.count}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  background: 'var(--bg)',
  border: '1px solid var(--border)',
  borderRadius: 12,
  padding: 20,
};

const rowStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  padding: '10px 0',
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

const btnSmallStyle: React.CSSProperties = {
  padding: '3px 8px',
  borderRadius: 4,
  border: 'none',
  background: 'none',
  color: 'var(--text)',
  fontSize: 12,
  fontWeight: 500,
  cursor: 'pointer',
  fontFamily: 'var(--sans)',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: 13,
  fontWeight: 500,
  color: 'var(--text-h)',
  marginBottom: 4,
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

export default TeamManager;
