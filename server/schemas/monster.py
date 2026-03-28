from pydantic import BaseModel


class DetectionSignal(BaseModel):
    pattern_zh: str
    pattern_en: str


class MonsterDefinition(BaseModel):
    id: str
    name_zh: str
    name_en: str
    emoji: str
    category: str  # communication | behavior | structural
    description_zh: str
    description_en: str
    mechanism_zh: str
    mechanism_en: str
    detection_signals: list[DetectionSignal]
    classic_lines_zh: list[str]
    classic_lines_en: list[str]
    severity_range: list[int]  # [min, max]


class MonsterDetected(BaseModel):
    monster_id: str
    monster_name_zh: str
    monster_name_en: str
    emoji: str
    severity: int  # 1-4
    evidence: list[str]
    explanation_zh: str
    explanation_en: str
    confidence: float  # 0-1
