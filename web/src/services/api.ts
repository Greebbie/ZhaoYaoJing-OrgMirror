export const API_BASE = import.meta.env.VITE_API_BASE || '';

export interface MirrorInput {
  content: string;
  content_type: 'chat_log' | 'meeting_notes' | 'email_thread' | 'requirement_doc' | 'self_check' | 'free_text';
  language: 'zh' | 'en' | 'auto';
  trigger_mode: string;
  anonymous_mode: boolean;
}

export interface Translation {
  original: string;
  mirror: string;
  monster_type: string | null;
  confidence: number;
}

export interface MonsterDetected {
  monster_id: string;
  monster_name_zh: string;
  monster_name_en: string;
  emoji: string;
  severity: number;
  evidence: string[];
  explanation_zh: string;
  explanation_en: string;
  confidence: number;
}

export interface HealthScore {
  overall: number;
  dimensions: {
    clarity: number;
    accountability: number;
    momentum: number;
    trust: number;
  };
}

export interface Recommendation {
  priority: string;
  action_zh: string;
  action_en: string;
  rationale_zh: string;
  rationale_en: string;
  addressed_monsters: string[];
}

export interface MirrorReport {
  translations: Translation[];
  monsters_detected: MonsterDetected[];
  xray: unknown | null;
  health_score: HealthScore | null;
  recommendations: Recommendation[];
}

export interface SelfMirrorResult {
  patterns_detected: Array<{
    pattern: string;
    description_zh: string;
    description_en: string;
    severity: number;
  }>;
  suggested_rewrite: string;
  comparison: {
    original_score: number;
    rewrite_score: number;
    improvements: string[];
  };
}

function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return 'Unexpected error';
}

export async function analyzeMirror(input: MirrorInput): Promise<MirrorReport> {
  try {
    const resp = await fetch(`${API_BASE}/api/mirror`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    if (!resp.ok) {
      throw new Error(`Mirror API error: ${resp.status}`);
    }
    return resp.json() as Promise<MirrorReport>;
  } catch (error: unknown) {
    throw new Error(`Mirror analysis failed: ${getErrorMessage(error)}`);
  }
}

export async function analyzeSelfMirror(
  content: string,
  language: string = 'auto'
): Promise<SelfMirrorResult> {
  try {
    const resp = await fetch(`${API_BASE}/api/self-mirror`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, language }),
    });
    if (!resp.ok) {
      throw new Error(`Self-Mirror API error: ${resp.status}`);
    }
    return resp.json() as Promise<SelfMirrorResult>;
  } catch (error: unknown) {
    throw new Error(`Self-mirror analysis failed: ${getErrorMessage(error)}`);
  }
}

export async function analyzeXray(
  content: string,
  content_type: string
): Promise<unknown> {
  try {
    const resp = await fetch(`${API_BASE}/api/xray`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content, content_type }),
    });
    if (!resp.ok) {
      throw new Error(`X-ray API error: ${resp.status}`);
    }
    return resp.json();
  } catch (error: unknown) {
    throw new Error(`X-ray analysis failed: ${getErrorMessage(error)}`);
  }
}
