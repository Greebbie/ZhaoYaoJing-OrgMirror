from pathlib import Path

from server.monsters.codex import MonsterCodex


def test_codex_loads_all_monsters():
    codex = MonsterCodex()
    codex.load()
    assert codex.count == 17, f"Expected 17 monsters, got {codex.count}"


def test_codex_categories():
    codex = MonsterCodex()
    codex.load()
    communication = codex.by_category("communication")
    behavior = codex.by_category("behavior")
    structural = codex.by_category("structural")
    assert len(communication) == 6
    assert len(behavior) == 6
    assert len(structural) == 5


def test_codex_lookup_by_id():
    codex = MonsterCodex()
    codex.load()
    phantom = codex.get("phantom_ally")
    assert phantom is not None
    assert phantom.name_zh == "社交性支持妖"
    assert phantom.emoji == "👻"
    assert phantom.category == "communication"


def test_codex_nonexistent_id():
    codex = MonsterCodex()
    codex.load()
    assert codex.get("nonexistent_monster") is None


def test_codex_monster_fields():
    codex = MonsterCodex()
    codex.load()
    for monster in codex.all_monsters:
        assert monster.id
        assert monster.name_zh
        assert monster.name_en
        assert monster.emoji
        assert monster.category in ("communication", "behavior", "structural")
        assert monster.description_zh
        assert monster.description_en
        assert monster.mechanism_zh
        assert monster.mechanism_en
        assert len(monster.detection_signals) > 0
        assert len(monster.severity_range) == 2
        assert 1 <= monster.severity_range[0] <= 4
        assert 1 <= monster.severity_range[1] <= 4


def test_codex_prompt_context():
    codex = MonsterCodex()
    codex.load()
    ctx_zh = codex.to_prompt_context("zh")
    assert "社交性支持妖" in ctx_zh
    assert "phantom_ally" in ctx_zh
    ctx_en = codex.to_prompt_context("en")
    assert "Phantom Ally" in ctx_en


def test_codex_custom_config_dir():
    codex = MonsterCodex()
    config_dir = Path(__file__).parent.parent / "config" / "monsters"
    codex.load(config_dir)
    assert codex.count == 17
