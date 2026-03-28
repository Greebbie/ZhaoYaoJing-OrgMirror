"""Feishu interactive message card builders.

Each function produces a card dict following Feishu's Interactive Message Card
protocol.  The top-level shape is:

    {
        "msg_type": "interactive",
        "card": {
            "header": { ... },
            "elements": [ ... ]
        }
    }

See https://open.feishu.cn/document/common-capabilities/message-card/overview
"""

from typing import Any

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_BADGE: dict[int, str] = {
    1: "\u26aa\ufe0f \u4f4e",       # white circle Low
    2: "\ud83d\udfe1 \u4e2d",       # yellow circle Medium
    3: "\ud83d\udfe0 \u9ad8",       # orange circle High
    4: "\ud83d\udd34 \u4e25\u91cd", # red circle Critical
}

_PRIORITY_COLOR: dict[str, str] = {
    "high": "\ud83d\udd34",    # red circle
    "medium": "\ud83d\udfe1",  # yellow circle
    "low": "\u26aa\ufe0f",     # white circle
}

_DIMENSION_LABELS: dict[str, str] = {
    "clarity": "\ud83d\udd0d \u6e05\u6670\u5ea6 (Clarity)",
    "accountability": "\ud83c\udfaf \u8d23\u4efb\u611f (Accountability)",
    "momentum": "\ud83d\ude80 \u52a8\u529b (Momentum)",
    "trust": "\ud83e\udd1d \u4fe1\u4efb (Trust)",
}


def _md(content: str) -> dict[str, str]:
    """Shorthand for a lark_md text node."""
    return {"tag": "lark_md", "content": content}


def _plain(content: str) -> dict[str, str]:
    """Shorthand for a plain_text node."""
    return {"tag": "plain_text", "content": content}


def _div(md_content: str) -> dict[str, Any]:
    """Shorthand for a div element with lark_md text."""
    return {"tag": "div", "text": _md(md_content)}


def _hr() -> dict[str, str]:
    return {"tag": "hr"}


def _button(label: str, btn_type: str = "default", value: dict | None = None) -> dict:
    return {
        "tag": "button",
        "text": _plain(label),
        "type": btn_type,
        "value": value or {},
    }


def _score_bar(score: int) -> str:
    """Build a visual score bar like: [========--] 80."""
    filled = round(score / 10)
    empty = 10 - filled
    return f"[{'=' * filled}{'-' * empty}] **{score}**"


# ---------------------------------------------------------------------------
# Public card builders
# ---------------------------------------------------------------------------


def build_mirror_report_card(report: dict, language: str = "zh") -> dict:
    """Build the full mirror report card.

    Args:
        report: Serialised MirrorReport dict with keys: translations,
                monsters_detected, health_score, recommendations.
        language: Display language ("zh" or "en").

    Returns:
        Feishu interactive message card dict.
    """
    elements: list[dict] = []

    # --- Translations section ---
    translations: list[dict] = report.get("translations", [])
    if translations:
        lines: list[str] = []
        for idx, t in enumerate(translations, 1):
            original = t.get("original", "")
            mirror = t.get("mirror", "")
            monster_tag = ""
            if t.get("monster_type"):
                monster_tag = f"  `{t['monster_type']}`"
            lines.append(f"{idx}. {original}\n   -> **{mirror}**{monster_tag}")
        # Collapse if more than 3
        if len(translations) > 3:
            collapsed_lines = "\n".join(lines[:3])
            remaining = "\n".join(lines[3:])
            elements.append(
                _div(f"**\ud83d\udd04 \u7ffb\u8bd1\u5bf9\u7167 (Translation)**\n{collapsed_lines}")
            )
            elements.append(
                _div(f"<details><summary>\u5c55\u5f00\u66f4\u591a ({len(translations) - 3} \u6761)...</summary>\n{remaining}\n</details>")
            )
        else:
            elements.append(
                _div("**\ud83d\udd04 \u7ffb\u8bd1\u5bf9\u7167 (Translation)**\n" + "\n".join(lines))
            )
        elements.append(_hr())

    # --- Monsters section ---
    monsters: list[dict] = report.get("monsters_detected", [])
    if monsters:
        monster_lines: list[str] = []
        for m in monsters:
            emoji = m.get("emoji", "\ud83d\udc7e")
            name = m.get("monster_name_zh", m.get("monster_id", ""))
            severity = m.get("severity", 1)
            badge = _SEVERITY_BADGE.get(severity, str(severity))
            confidence = m.get("confidence", 0)
            monster_lines.append(
                f"- {emoji} **{name}**  {badge}  "
                f"(\u7f6e\u4fe1\u5ea6 {confidence:.0%})"
            )
        elements.append(
            _div(
                "**\ud83d\udc7e \u68c0\u6d4b\u5230\u7684\u5996\u602a (Monsters Detected)**\n"
                + "\n".join(monster_lines)
            )
        )
        elements.append(_hr())

    # --- Health score section ---
    health: dict | None = report.get("health_score")
    if health:
        overall = health.get("overall", 0)
        dims = health.get("dimensions", {})
        dim_lines = [
            f"- {_DIMENSION_LABELS.get(k, k)}: {_score_bar(v)}"
            for k, v in dims.items()
            if k in _DIMENSION_LABELS
        ]
        elements.append(
            _div(
                f"**\u2764\ufe0f \u7ec4\u7ec7\u5065\u5eb7\u5206 (Health Score): {_score_bar(overall)}**\n"
                + "\n".join(dim_lines)
            )
        )
        elements.append(_hr())

    # --- Recommendations section ---
    recs: list[dict] = report.get("recommendations", [])
    if recs:
        rec_lines: list[str] = []
        for r in recs:
            priority = r.get("priority", "medium")
            icon = _PRIORITY_COLOR.get(priority, "")
            action = r.get("action_zh", "") if language == "zh" else r.get("action_en", "")
            rec_lines.append(f"- {icon} **[{priority.upper()}]** {action}")
        elements.append(
            _div(
                "**\ud83d\udca1 \u6539\u8fdb\u5efa\u8bae (Recommendations)**\n"
                + "\n".join(rec_lines)
            )
        )
        elements.append(_hr())

    # --- Action buttons ---
    elements.append(
        {
            "tag": "action",
            "actions": [
                _button(
                    "\ud83d\udcdd \u67e5\u770b\u5b8c\u6574\u62a5\u544a",
                    btn_type="primary",
                    value={"action": "view_full_report"},
                ),
                _button(
                    "\ud83d\udcf8 \u751f\u6210X\u5149\u7247",
                    btn_type="default",
                    value={"action": "generate_xray"},
                ),
            ],
        }
    )

    # --- Footnote ---
    elements.append(
        {
            "tag": "note",
            "elements": [
                _md(
                    "\u7167\u5996\u955c v0.1 \u00b7 "
                    "\u5206\u6790\u7ed3\u679c\u4ec5\u4f9b\u53c2\u8003\uff0c"
                    "\u8bf7\u7ed3\u5408\u5b9e\u9645\u60c5\u666f\u5224\u65ad"
                ),
            ],
        }
    )

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": _plain("\ud83e\ude9e \u7167\u5996\u955c\u5206\u6790\u62a5\u544a"),
                "template": "blue",
            },
            "elements": elements,
        },
    }


def build_monster_card(monster: dict) -> dict:
    """Build a card for a single detected monster.

    Args:
        monster: Serialised MonsterDetected dict.

    Returns:
        Feishu interactive message card dict.
    """
    emoji = monster.get("emoji", "\ud83d\udc7e")
    name_zh = monster.get("monster_name_zh", "")
    name_en = monster.get("monster_name_en", "")
    severity = monster.get("severity", 1)
    badge = _SEVERITY_BADGE.get(severity, str(severity))
    evidence = monster.get("evidence", [])
    explanation = monster.get("explanation_zh", "")

    evidence_md = "\n".join(f"- {e}" for e in evidence) if evidence else "- \u65e0"

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": _plain(f"{emoji} {name_zh} ({name_en})"),
                "template": "orange",
            },
            "elements": [
                _div(f"**\u4e25\u91cd\u5ea6:** {badge}"),
                _hr(),
                _div(f"**\ud83d\udd0d \u8bc1\u636e (Evidence)**\n{evidence_md}"),
                _hr(),
                _div(f"**\ud83d\udcac \u89e3\u8bfb**\n{explanation}"),
                {
                    "tag": "note",
                    "elements": [
                        _md(
                            "\u7167\u5996\u955c\u00b7"
                            "\u5996\u602a\u8be6\u60c5"
                        ),
                    ],
                },
            ],
        },
    }


def build_xray_card(xray: dict) -> dict:
    """Build an X-ray card for a work item.

    Args:
        xray: Serialised XRay dict with keys: objective, deadline, owner,
              dependencies, success_criteria, missing_info, blockers.

    Returns:
        Feishu interactive message card dict.
    """
    objective = xray.get("objective", "unclear")
    deadline = xray.get("deadline", "unspecified")
    owner = xray.get("owner", "unassigned")
    blockers = xray.get("blockers", [])
    missing_info = xray.get("missing_info", [])
    dependencies = xray.get("dependencies", [])
    success_criteria = xray.get("success_criteria", "undefined")

    blockers_md = "\n".join(f"- {b}" for b in blockers) if blockers else "- \u65e0"
    missing_md = "\n".join(f"- {m}" for m in missing_info) if missing_info else "- \u65e0"
    deps_md = "\n".join(f"- {d}" for d in dependencies) if dependencies else "- \u65e0"

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": _plain("\ud83d\udcf8 X\u5149\u7247\u900f\u89c6"),
                "template": "purple",
            },
            "elements": [
                _div(
                    f"**\ud83c\udfaf \u76ee\u6807 (Objective):** {objective}\n"
                    f"**\u23f0 \u622a\u6b62\u65e5\u671f (Deadline):** {deadline}\n"
                    f"**\ud83d\udc64 \u8d1f\u8d23\u4eba (Owner):** {owner}\n"
                    f"**\u2705 \u6210\u529f\u6807\u51c6 (Success Criteria):** {success_criteria}"
                ),
                _hr(),
                _div(f"**\ud83d\udee3\ufe0f \u4f9d\u8d56 (Dependencies)**\n{deps_md}"),
                _hr(),
                _div(f"**\ud83d\udeab \u963b\u585e\u9879 (Blockers)**\n{blockers_md}"),
                _hr(),
                _div(f"**\u2753 \u7f3a\u5931\u4fe1\u606f (Missing Info)**\n{missing_md}"),
                {
                    "tag": "note",
                    "elements": [
                        _md(
                            "\u7167\u5996\u955c\u00b7"
                            "X\u5149\u7247\u900f\u89c6"
                        ),
                    ],
                },
            ],
        },
    }


def build_self_check_card(result: dict) -> dict:
    """Build a self-check result card (sent as private message).

    Args:
        result: Serialised SelfMirrorResult dict with keys:
                patterns_detected, suggested_rewrite, improvement_notes_zh.

    Returns:
        Feishu interactive message card dict.
    """
    patterns = result.get("patterns_detected", [])
    rewrite = result.get("suggested_rewrite", "")
    notes = result.get("improvement_notes_zh", result.get("improvement_notes_en", ""))

    pattern_lines: list[str] = []
    for p in patterns:
        monster_id = p.get("monster_id", "")
        segment = p.get("text_segment", "")
        issue = p.get("issue_zh", p.get("issue_en", ""))
        pattern_lines.append(f"- `{monster_id}` **{segment}**\n  {issue}")

    patterns_md = "\n".join(pattern_lines) if pattern_lines else "- \u672a\u68c0\u6d4b\u5230\u95ee\u9898\uff0c\u5f88\u597d\uff01"

    elements: list[dict] = [
        _div(f"**\ud83d\udd0d \u68c0\u6d4b\u5230\u7684\u6a21\u5f0f (Patterns)**\n{patterns_md}"),
        _hr(),
        _div(f"**\u270f\ufe0f \u5efa\u8bae\u6539\u5199 (Suggested Rewrite)**\n{rewrite}"),
        _hr(),
        _div(f"**\ud83d\udcdd \u6539\u8fdb\u8bf4\u660e**\n{notes}"),
        {
            "tag": "note",
            "elements": [
                _md(
                    "\u7167\u5996\u955c\u00b7"
                    "\u81ea\u67e5\u7ed3\u679c\u4ec5\u4f60\u53ef\u89c1"
                ),
            ],
        },
    ]

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": _plain("\ud83e\ude9e \u81ea\u67e5\u7ed3\u679c (Self-Check)"),
                "template": "green",
            },
            "elements": elements,
        },
    }
