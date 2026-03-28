import logging
from pathlib import Path

import yaml

from server.schemas.monster import DetectionSignal, MonsterDefinition

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent.parent / "config" / "monsters"


class MonsterCodex:
    """Loads and manages the Monster Codex from YAML files."""

    def __init__(self):
        self._monsters: dict[str, MonsterDefinition] = {}
        self._by_category: dict[str, list[MonsterDefinition]] = {}

    def load(self, config_dir: Path | None = None):
        base = config_dir or CONFIG_DIR
        for subdir in ["builtin", "community"]:
            monster_dir = base / subdir
            if not monster_dir.exists():
                continue
            for yaml_file in sorted(monster_dir.glob("*.yaml")):
                self._load_file(yaml_file)
        logger.info("Loaded %d monsters from codex", len(self._monsters))

    def _load_file(self, path: Path):
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or "monsters" not in data:
            return
        for entry in data["monsters"]:
            signals = [
                DetectionSignal(**s)
                for s in entry.get("detection_signals", [])
            ]
            monster = MonsterDefinition(
                id=entry["id"],
                name_zh=entry["name_zh"],
                name_en=entry["name_en"],
                emoji=entry["emoji"],
                category=entry["category"],
                description_zh=entry["description_zh"],
                description_en=entry["description_en"],
                mechanism_zh=entry["mechanism_zh"],
                mechanism_en=entry["mechanism_en"],
                detection_signals=signals,
                classic_lines_zh=entry.get("classic_lines_zh", []),
                classic_lines_en=entry.get("classic_lines_en", []),
                severity_range=entry.get("severity_range", [1, 2]),
            )
            self._monsters[monster.id] = monster
            self._by_category.setdefault(monster.category, []).append(monster)

    @property
    def all_monsters(self) -> list[MonsterDefinition]:
        return list(self._monsters.values())

    def get(self, monster_id: str) -> MonsterDefinition | None:
        return self._monsters.get(monster_id)

    def by_category(self, category: str) -> list[MonsterDefinition]:
        return self._by_category.get(category, [])

    def by_severity_min(self, min_severity: int) -> list[MonsterDefinition]:
        return [m for m in self._monsters.values() if m.severity_range[0] >= min_severity]

    def to_prompt_context(self, language: str = "zh") -> str:
        """Format all monsters as context for LLM prompts."""
        lines = []
        for m in self._monsters.values():
            if language == "en":
                lines.append(
                    f"- {m.emoji} {m.name_en} (ID: {m.id}): {m.description_en}. "
                    f"Mechanism: {m.mechanism_en}. "
                    f"Classic lines: {'; '.join(m.classic_lines_en)}"
                )
            else:
                lines.append(
                    f"- {m.emoji} {m.name_zh} (ID: {m.id}): {m.description_zh}. "
                    f"机制: {m.mechanism_zh}. "
                    f"经典台词: {'；'.join(m.classic_lines_zh)}"
                )
        return "\n".join(lines)

    @property
    def count(self) -> int:
        return len(self._monsters)


# Singleton
monster_codex = MonsterCodex()
monster_codex.load()
