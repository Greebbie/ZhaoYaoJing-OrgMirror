"""WeCom message templates using Markdown format.

WeCom supports Markdown in application messages. Each function produces a plain
Markdown string suitable for sending via the WeCom message API.
"""

# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_BADGE: dict[int, str] = {
    1: "\u26aa\ufe0f \u4f4e",       # white circle Low
    2: "\ud83d\udfe1 \u4e2d",       # yellow circle Medium
    3: "\ud83d\udfe0 \u9ad8",       # orange circle High
    4: "\ud83d\udd34 \u4e25\u91cd", # red circle Critical
}

_PRIORITY_ICON: dict[str, str] = {
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


def _score_bar(score: int) -> str:
    """Build a visual score bar like: [========--] 80."""
    filled = round(score / 10)
    empty = 10 - filled
    return f"[{'=' * filled}{'-' * empty}] **{score}**"


# ---------------------------------------------------------------------------
# Public template builders
# ---------------------------------------------------------------------------


def build_mirror_report_md(report: dict, language: str = "zh") -> str:
    """Build the full mirror report as Markdown.

    Args:
        report: Serialised MirrorReport dict with keys: translations,
                monsters_detected, health_score, recommendations.
        language: Display language ("zh" or "en").

    Returns:
        Markdown formatted string.
    """
    sections: list[str] = []

    # --- Header ---
    sections.append("# \ud83e\ude9e \u7167\u5996\u955c\u5206\u6790\u62a5\u544a\n")

    # --- Translations section ---
    translations: list[dict] = report.get("translations", [])
    if translations:
        lines: list[str] = ["## \ud83d\udd04 \u7ffb\u8bd1\u5bf9\u7167 (Translation)\n"]
        for idx, t in enumerate(translations, 1):
            original = t.get("original", "")
            mirror = t.get("mirror", "")
            monster_tag = ""
            if t.get("monster_type"):
                monster_tag = f"  `{t['monster_type']}`"
            lines.append(f"{idx}. {original}\n   > **{mirror}**{monster_tag}")
        sections.append("\n".join(lines))

    # --- Monsters section ---
    monsters: list[dict] = report.get("monsters_detected", [])
    if monsters:
        monster_lines: list[str] = [
            "## \ud83d\udc7e \u68c0\u6d4b\u5230\u7684\u5996\u602a (Monsters Detected)\n",
        ]
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
        sections.append("\n".join(monster_lines))

    # --- Health score section ---
    health: dict | None = report.get("health_score")
    if health:
        overall = health.get("overall", 0)
        dims = health.get("dimensions", {})
        health_lines: list[str] = [
            f"## \u2764\ufe0f \u7ec4\u7ec7\u5065\u5eb7\u5206 (Health Score): {_score_bar(overall)}\n",
        ]
        for k, v in dims.items():
            label = _DIMENSION_LABELS.get(k, k)
            health_lines.append(f"- {label}: {_score_bar(v)}")
        sections.append("\n".join(health_lines))

    # --- Recommendations section ---
    recs: list[dict] = report.get("recommendations", [])
    if recs:
        rec_lines: list[str] = [
            "## \ud83d\udca1 \u6539\u8fdb\u5efa\u8bae (Recommendations)\n",
        ]
        for r in recs:
            priority = r.get("priority", "medium")
            icon = _PRIORITY_ICON.get(priority, "")
            action = (
                r.get("action_zh", "")
                if language == "zh"
                else r.get("action_en", "")
            )
            rec_lines.append(f"- {icon} **[{priority.upper()}]** {action}")
        sections.append("\n".join(rec_lines))

    # --- Footnote ---
    sections.append(
        "---\n"
        "\u7167\u5996\u955c v0.1 \u00b7 "
        "\u5206\u6790\u7ed3\u679c\u4ec5\u4f9b\u53c2\u8003\uff0c"
        "\u8bf7\u7ed3\u5408\u5b9e\u9645\u60c5\u666f\u5224\u65ad"
    )

    return "\n\n".join(sections)


def build_xray_md(xray: dict) -> str:
    """Build an X-ray result as Markdown.

    Args:
        xray: Serialised XRay dict with keys: objective, deadline, owner,
              dependencies, success_criteria, missing_info, blockers.

    Returns:
        Markdown formatted string.
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

    return (
        "# \ud83d\udcf8 X\u5149\u7247\u900f\u89c6\n\n"
        f"**\ud83c\udfaf \u76ee\u6807 (Objective):** {objective}\n"
        f"**\u23f0 \u622a\u6b62\u65e5\u671f (Deadline):** {deadline}\n"
        f"**\ud83d\udc64 \u8d1f\u8d23\u4eba (Owner):** {owner}\n"
        f"**\u2705 \u6210\u529f\u6807\u51c6 (Success Criteria):** {success_criteria}\n\n"
        f"## \ud83d\udee3\ufe0f \u4f9d\u8d56 (Dependencies)\n{deps_md}\n\n"
        f"## \ud83d\udeab \u963b\u585e\u9879 (Blockers)\n{blockers_md}\n\n"
        f"## \u2753 \u7f3a\u5931\u4fe1\u606f (Missing Info)\n{missing_md}\n\n"
        "---\n"
        "\u7167\u5996\u955c\u00b7X\u5149\u7247\u900f\u89c6"
    )


def build_self_check_md(result: dict) -> str:
    """Build a self-check result as Markdown (sent as private message).

    Args:
        result: Serialised SelfMirrorResult dict with keys:
                patterns_detected, suggested_rewrite, improvement_notes_zh.

    Returns:
        Markdown formatted string.
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
        pattern_lines.append(f"- `{monster_id}` **{segment}**\n  {issue}")

    patterns_md = (
        "\n".join(pattern_lines)
        if pattern_lines
        else "- \u672a\u68c0\u6d4b\u5230\u95ee\u9898\uff0c\u5f88\u597d\uff01"
    )

    return (
        "# \ud83e\ude9e \u81ea\u67e5\u7ed3\u679c (Self-Check)\n\n"
        f"## \ud83d\udd0d \u68c0\u6d4b\u5230\u7684\u6a21\u5f0f (Patterns)\n{patterns_md}\n\n"
        f"## \u270f\ufe0f \u5efa\u8bae\u6539\u5199 (Suggested Rewrite)\n{rewrite}\n\n"
        f"## \ud83d\udcdd \u6539\u8fdb\u8bf4\u660e\n{notes}\n\n"
        "---\n"
        "\u7167\u5996\u955c\u00b7\u81ea\u67e5\u7ed3\u679c\u4ec5\u4f60\u53ef\u89c1"
    )
