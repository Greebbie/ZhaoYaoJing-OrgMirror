"""Trigger rule definitions and YAML loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class TriggerRule(BaseModel):
    """Schema for a single trigger rule loaded from YAML config."""

    id: str
    type: str
    description_zh: str = ""
    description_en: str = ""
    condition: dict[str, Any] = Field(default_factory=dict)
    action: str = ""
    visibility: str = "thread"
    enabled: bool = True


_DEFAULT_RULES_PATH = (
    Path(__file__).resolve().parent.parent.parent / "config" / "triggers" / "rules.yaml"
)


def load_rules(path: Path | str | None = None) -> list[TriggerRule]:
    """Load trigger rules from a YAML file.

    Args:
        path: Path to the YAML file. Falls back to ``config/triggers/rules.yaml``.

    Returns:
        A list of validated ``TriggerRule`` objects.

    Raises:
        FileNotFoundError: If the rules file does not exist.
        ValueError: If the YAML structure is invalid.
    """
    rules_path = Path(path) if path is not None else _DEFAULT_RULES_PATH

    if not rules_path.exists():
        raise FileNotFoundError(f"Trigger rules file not found: {rules_path}")

    raw = yaml.safe_load(rules_path.read_text(encoding="utf-8"))

    if not isinstance(raw, dict) or "triggers" not in raw:
        raise ValueError(
            f"Invalid rules file structure: expected top-level 'triggers' key in {rules_path}"
        )

    raw_triggers = raw["triggers"]
    if not isinstance(raw_triggers, list):
        raise ValueError("'triggers' must be a list")

    return [TriggerRule.model_validate(entry) for entry in raw_triggers]
