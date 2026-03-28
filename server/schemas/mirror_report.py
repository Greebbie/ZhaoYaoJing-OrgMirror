from pydantic import BaseModel

from server.schemas.monster import MonsterDetected


class Translation(BaseModel):
    original: str
    mirror: str
    monster_type: str | None = None
    confidence: float  # 0-1


class XRay(BaseModel):
    objective: str  # "unclear" if not determinable
    deadline: str  # "unspecified" if not set
    owner: str  # "unassigned" if not set
    dependencies: list[str]
    success_criteria: str  # "undefined" if not set
    missing_info: list[str]
    blockers: list[str]


class HealthDimensions(BaseModel):
    clarity: int  # 0-100
    accountability: int  # 0-100
    momentum: int  # 0-100
    trust: int  # 0-100


class HealthScore(BaseModel):
    overall: int  # 0-100
    dimensions: HealthDimensions


class Recommendation(BaseModel):
    priority: str  # high | medium | low
    action_zh: str
    action_en: str
    rationale_zh: str
    rationale_en: str
    addressed_monsters: list[str]


class MirrorReport(BaseModel):
    translations: list[Translation]
    monsters_detected: list[MonsterDetected]
    xray: XRay | None = None
    health_score: HealthScore | None = None
    recommendations: list[Recommendation] = []
