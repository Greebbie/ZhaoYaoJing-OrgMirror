# Contributing to ZhaoYaoJing / 贡献指南

## Contribution Paths / 贡献路径

| Type | Difficulty | Entry Point |
|------|-----------|-------------|
| Submit new monster / 提交新妖怪 | Easy | YAML + PR |
| Submit translation samples / 提交照妖翻译语料 | Easy | Issue or form |
| Improve detection prompts / 改进检测 Prompt | Medium | PR to `server/prompts/` |
| Add bot adapter / 新增 Bot 适配 | Hard | PR to `bots/` |
| Improve agent protocols / 改进 Agent 协议 | Expert | PR to `server/agents/` |
| Add LLM provider / 新增模型后端 | Medium | PR to `server/llm/` |

## Submitting a New Monster / 提交新妖怪

The easiest and most impactful way to contribute. Create a YAML file in `config/monsters/community/`:

```yaml
id: your_monster_id                    # Unique, snake_case
name_zh: "妖怪中文名"
name_en: "Monster English Name"
category: communication                # communication | behavior | structural
description_zh: "中文描述"
description_en: "English description"
detection_signals:
  - pattern_zh: "中文检测模式"
    pattern_en: "English detection pattern"
classic_lines_zh:
  - "经典台词中文"
classic_lines_en:
  - "Classic line English"
severity_range: [1, 2]                 # Min and max severity (1-4)
contributed_by: "your_github_username"
```

Validate your monster:
```bash
python scripts/validate_monster.py config/monsters/community/your_monster.yaml
```

## Development Setup / 开发环境

```bash
# Backend
cd server
pip install -e ".[dev]"
uvicorn main:app --reload

# Frontend
cd web
npm install
npm run dev

# Tests
pytest

# Lint
ruff check server/
```

## Code Style / 代码规范

- Python: follow ruff defaults, type hints required
- TypeScript: strict mode, functional components
- Commits: conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`)
- Bilingual: all user-facing strings must have both Chinese and English versions

## Pull Request Process / PR 流程

1. Fork the repo
2. Create a feature branch (`feat/your-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Ensure lint passes (`ruff check server/`)
6. Submit PR with clear description

## License / 许可

By contributing, you agree that your contributions will be licensed under the MIT License.
