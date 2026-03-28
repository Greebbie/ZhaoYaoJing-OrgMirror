"""Slack Block Kit message builders.

Each function produces a list of Block Kit block dicts following Slack's
Block Kit protocol.

See https://api.slack.com/reference/block-kit/blocks
"""

from typing import Any

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_BADGE: dict[int, str] = {
    1: "\u26aa\ufe0f Low",
    2: "\ud83d\udfe1 Medium",
    3: "\ud83d\udfe0 High",
    4: "\ud83d\udd34 Critical",
}

_PRIORITY_ICON: dict[str, str] = {
    "high": "\ud83d\udd34",    # red circle
    "medium": "\ud83d\udfe1",  # yellow circle
    "low": "\u26aa\ufe0f",     # white circle
}

_DIMENSION_LABELS: dict[str, str] = {
    "clarity": "\ud83d\udd0d Clarity",
    "accountability": "\ud83c\udfaf Accountability",
    "momentum": "\ud83d\ude80 Momentum",
    "trust": "\ud83e\udd1d Trust",
}


def _header(text: str) -> dict[str, Any]:
    """Build a header block."""
    return {
        "type": "header",
        "text": {"type": "plain_text", "text": text, "emoji": True},
    }


def _section(text: str) -> dict[str, Any]:
    """Build a section block with mrkdwn text."""
    return {
        "type": "section",
        "text": {"type": "mrkdwn", "text": text},
    }


def _divider() -> dict[str, str]:
    """Build a divider block."""
    return {"type": "divider"}


def _context(text: str) -> dict[str, Any]:
    """Build a context block with mrkdwn text."""
    return {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": text}],
    }


def _button(
    text: str,
    action_id: str,
    value: str = "",
    style: str | None = None,
) -> dict[str, Any]:
    """Build a button element."""
    btn: dict[str, Any] = {
        "type": "button",
        "text": {"type": "plain_text", "text": text, "emoji": True},
        "action_id": action_id,
        "value": value,
    }
    if style in ("primary", "danger"):
        btn["style"] = style
    return btn


def _score_bar(score: int) -> str:
    """Build a visual score bar like: [========--] 80."""
    filled = round(score / 10)
    empty = 10 - filled
    return f"`[{'=' * filled}{'-' * empty}]` *{score}*"


# ---------------------------------------------------------------------------
# Public block builders
# ---------------------------------------------------------------------------


def build_mirror_report_blocks(
    report: dict,
    language: str = "zh",
) -> list[dict]:
    """Build Block Kit blocks for the mirror report.

    Args:
        report: Serialised MirrorReport dict with keys: translations,
                monsters_detected, health_score, recommendations.
        language: Display language ("zh" or "en").

    Returns:
        List of Slack Block Kit block dicts.
    """
    blocks: list[dict] = []

    blocks.append(_header("\ud83e\ude9e \u7167\u5996\u955c\u5206\u6790\u62a5\u544a"))

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
            lines.append(f"{idx}. {original}\n    > *{mirror}*{monster_tag}")
        blocks.append(
            _section(
                "*\ud83d\udd04 \u7ffb\u8bd1\u5bf9\u7167 (Translation)*\n"
                + "\n".join(lines)
            )
        )
        blocks.append(_divider())

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
                f"\u2022 {emoji} *{name}*  {badge}  "
                f"(\u7f6e\u4fe1\u5ea6 {confidence:.0%})"
            )
        blocks.append(
            _section(
                "*\ud83d\udc7e \u68c0\u6d4b\u5230\u7684\u5996\u602a (Monsters Detected)*\n"
                + "\n".join(monster_lines)
            )
        )
        blocks.append(_divider())

    # --- Health score section ---
    health: dict | None = report.get("health_score")
    if health:
        overall = health.get("overall", 0)
        dims = health.get("dimensions", {})
        dim_lines = [
            f"\u2022 {_DIMENSION_LABELS.get(k, k)}: {_score_bar(v)}"
            for k, v in dims.items()
            if k in _DIMENSION_LABELS
        ]
        blocks.append(
            _section(
                f"*\u2764\ufe0f \u7ec4\u7ec7\u5065\u5eb7\u5206 (Health Score): {_score_bar(overall)}*\n"
                + "\n".join(dim_lines)
            )
        )
        blocks.append(_divider())

    # --- Recommendations section ---
    recs: list[dict] = report.get("recommendations", [])
    if recs:
        rec_lines: list[str] = []
        for r in recs:
            priority = r.get("priority", "medium")
            icon = _PRIORITY_ICON.get(priority, "")
            action = (
                r.get("action_zh", "")
                if language == "zh"
                else r.get("action_en", "")
            )
            rec_lines.append(f"\u2022 {icon} *[{priority.upper()}]* {action}")
        blocks.append(
            _section(
                "*\ud83d\udca1 \u6539\u8fdb\u5efa\u8bae (Recommendations)*\n"
                + "\n".join(rec_lines)
            )
        )
        blocks.append(_divider())

    # --- Action buttons ---
    blocks.append(
        {
            "type": "actions",
            "elements": [
                _button(
                    "\ud83d\udcdd \u67e5\u770b\u5b8c\u6574\u62a5\u544a",
                    action_id="view_full_report",
                    value="view_full_report",
                    style="primary",
                ),
                _button(
                    "\ud83d\udcf8 \u751f\u6210X\u5149\u7247",
                    action_id="generate_xray",
                    value="generate_xray",
                ),
            ],
        }
    )

    # --- Footnote ---
    blocks.append(
        _context(
            "\u7167\u5996\u955c v0.1 \u00b7 "
            "\u5206\u6790\u7ed3\u679c\u4ec5\u4f9b\u53c2\u8003\uff0c"
            "\u8bf7\u7ed3\u5408\u5b9e\u9645\u60c5\u666f\u5224\u65ad"
        )
    )

    return blocks


def build_xray_blocks(xray: dict) -> list[dict]:
    """Build Block Kit blocks for an X-ray result.

    Args:
        xray: Serialised XRay dict with keys: objective, deadline, owner,
              dependencies, success_criteria, missing_info, blockers.

    Returns:
        List of Slack Block Kit block dicts.
    """
    objective = xray.get("objective", "unclear")
    deadline = xray.get("deadline", "unspecified")
    owner = xray.get("owner", "unassigned")
    blockers = xray.get("blockers", [])
    missing_info = xray.get("missing_info", [])
    dependencies = xray.get("dependencies", [])
    success_criteria = xray.get("success_criteria", "undefined")

    blockers_md = "\n".join(f"\u2022 {b}" for b in blockers) if blockers else "\u2022 \u65e0"
    missing_md = "\n".join(f"\u2022 {m}" for m in missing_info) if missing_info else "\u2022 \u65e0"
    deps_md = "\n".join(f"\u2022 {d}" for d in dependencies) if dependencies else "\u2022 \u65e0"

    return [
        _header("\ud83d\udcf8 X\u5149\u7247\u900f\u89c6"),
        _section(
            f"*\ud83c\udfaf \u76ee\u6807 (Objective):* {objective}\n"
            f"*\u23f0 \u622a\u6b62\u65e5\u671f (Deadline):* {deadline}\n"
            f"*\ud83d\udc64 \u8d1f\u8d23\u4eba (Owner):* {owner}\n"
            f"*\u2705 \u6210\u529f\u6807\u51c6 (Success Criteria):* {success_criteria}"
        ),
        _divider(),
        _section(f"*\ud83d\udee3\ufe0f \u4f9d\u8d56 (Dependencies)*\n{deps_md}"),
        _divider(),
        _section(f"*\ud83d\udeab \u963b\u585e\u9879 (Blockers)*\n{blockers_md}"),
        _divider(),
        _section(f"*\u2753 \u7f3a\u5931\u4fe1\u606f (Missing Info)*\n{missing_md}"),
        _context(
            "\u7167\u5996\u955c\u00b7X\u5149\u7247\u900f\u89c6"
        ),
    ]


def build_self_check_blocks(result: dict) -> list[dict]:
    """Build Block Kit blocks for a self-check result (sent as DM).

    Args:
        result: Serialised SelfMirrorResult dict with keys:
                patterns_detected, suggested_rewrite, improvement_notes_zh.

    Returns:
        List of Slack Block Kit block dicts.
    """
    patterns = result.get("patterns_detected", [])
    rewrite = result.get("suggested_rewrite", "")
    notes = result.get(
        "improvement_notes_zh",
        result.get("improvement_notes_en", ""),
    )

    pattern_lines: list[str] = []
    for p in patterns:
        monster_id = p.get("monster_id", "")
        segment = p.get("text_segment", "")
        issue = p.get("issue_zh", p.get("issue_en", ""))
        pattern_lines.append(f"\u2022 `{monster_id}` *{segment}*\n  {issue}")

    patterns_md = (
        "\n".join(pattern_lines)
        if pattern_lines
        else "\u2022 \u672a\u68c0\u6d4b\u5230\u95ee\u9898\uff0c\u5f88\u597d\uff01"
    )

    return [
        _header("\ud83e\ude9e \u81ea\u67e5\u7ed3\u679c (Self-Check)"),
        _section(f"*\ud83d\udd0d \u68c0\u6d4b\u5230\u7684\u6a21\u5f0f (Patterns)*\n{patterns_md}"),
        _divider(),
        _section(f"*\u270f\ufe0f \u5efa\u8bae\u6539\u5199 (Suggested Rewrite)*\n{rewrite}"),
        _divider(),
        _section(f"*\ud83d\udcdd \u6539\u8fdb\u8bf4\u660e*\n{notes}"),
        _context(
            "\u7167\u5996\u955c\u00b7\u81ea\u67e5\u7ed3\u679c\u4ec5\u4f60\u53ef\u89c1"
        ),
    ]
