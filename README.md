<div align="center">

# ZhaoYaoJing - OrgMirror

### Strip the bullshit. See the real org.

### 把办公室里的妖魔鬼怪照出原形。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)

**[English](#english)** | **[中文](#中文)**

</div>

---

<a id="english"></a>

## What is ZhaoYaoJing?

An open-source AI framework that strips away organizational bullshit, detects collaboration dysfunction patterns, and makes it structurally harder for people to hide behind vague language, fake consensus, and accountability drift.

Not a project management tool. Not a Jira replacement. It's an **X-ray machine for organizational dysfunction**.

> Satire drives adoption. Diagnosis drives retention. Recommendations drive value.

### How it works

Paste any organizational communication (chat logs, meeting notes, emails) and get:

| Output | What it does |
|--------|-------------|
| **Mirror Translation** | Reveals what corporate speak actually means |
| **Monster Detection** | Identifies dysfunction patterns from the Monster Codex (17 named patterns) |
| **Health Score** | 4-dimension assessment: Clarity, Accountability, Momentum, Trust |
| **Recommendations** | Serious, actionable suggestions (not sarcastic) |
| **Deliberation** | Multi-party conflict resolution with AI advocates |

### Demo

![ZhaoYaoJing Demo](demo_page.png)

<details>
<summary><b>Example: What the mirror reveals</b></summary>

**Input:**
> "The data dashboard requirement was brought up by Lao Li before. I think the direction is right. But we're really short-staffed right now, Xiao Wang has two urgent things to handle first. I suggest we schedule a meeting next week, get product, frontend, and data people together, align on the specifics, then schedule it."

**Mirror Translation:**

| Original | Mirror |
|----------|--------|
| "I think the direction is right" | Verbal support. I won't do anything about it. |
| "We're short-staffed" | Resource veto activated. Using "tight resources" as a hidden veto. |
| "Let's schedule a meeting next week" | Meeting vortex initiated. Process replaces progress. |

**Monsters Detected:**
- 👻 **Phantom Ally** (Lv.2) — Verbal support with zero follow-up
- 🧱 **Resource Void** (Lv.2) — Using resources as implicit veto power
- 🌀 **Meeting Vortex** (Lv.2) — "Let's align" replaces actual decisions
- 🫥 **Blame Redirector** (Lv.1) — Citing absent person to deflect ownership

**Health Score: 34/100**

</details>

### Monster Codex (17 Built-in Patterns)

<details>
<summary><b>Communication Layer (6)</b></summary>

| Monster | What it does |
|---------|-------------|
| 🦊 **Eternal Evaluator** | Uses "evaluate" / "let's see" to avoid yes/no |
| 👻 **Phantom Ally** | Verbally supports, follows up with zero action |
| 🎭 **Ghost Mandate** | Claims untraceable upper-level authorization |
| 🎪 **Compliment Assassin** | Affirms then negates, making rebuttal impossible |
| 🏔️ **Big Picture Bully** | Uses "strategy" to suppress concrete needs |
| 🐌 **Gentle Vetoist** | "Let me think about it" = quiet no |

</details>

<details>
<summary><b>Behavior Layer (6)</b></summary>

| Monster | What it does |
|---------|-------------|
| 💨 **Diffusion Ghost** | No single owner, responsibility diluted |
| 🧱 **Resource Void** | Verbal resource commitment, never delivers |
| 🌀 **Meeting Vortex** | Substitutes meetings for actual progress |
| 🐌 **Ghost Owner** | Named owner who effectively vanishes |
| 📈 **Scope Creep Shield** | Adds prerequisites to kill initiatives |
| 🫥 **Blame Redirector** | Points responsibility at absent parties |

</details>

<details>
<summary><b>Structural Layer (5)</b></summary>

| Monster | What it does |
|---------|-------------|
| ⏰ **Sliding Deadline** | Deadline quietly shifts without announcement |
| 🔀 **Bypass Artist** | Goes around owner to higher authority |
| 🧬 **Mutation Drift** | Requirements silently rewritten during execution |
| 🏚️ **Legacy Blame** | "Historical reasons" = permanent excuse |
| 🎣 **Info Gatekeeper** | Selectively withholds information for power |

</details>

### Five Trigger Modes

```
 Naturalness
    ↑
    │  ⑤ Always-on: all items auto-scanned (most natural)
    │  ④ Event trigger: conditions met → auto-scan
    │  ③ Self-mirror: scan YOUR OWN message (neutral)
    │  ② @Bot: someone triggers in group chat
    │  ① Manual paste: copy text to web portal (most deliberate)
    └──────────────────────────────────────────▶ Integration Cost
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+ / FastAPI / SQLAlchemy |
| Frontend | React 19 / TypeScript / Vite |
| Database | SQLite (dev) / PostgreSQL (prod) |
| LLM | OpenAI / Qwen / Gemini / MiniMax (multi-provider with fallback) |
| Bots | Feishu / WeCom / Slack |
| Deploy | Docker Compose |

### Quick Start

```bash
git clone https://github.com/your-org/zhaoyaojing.git
cd zhaoyaojing

cp .env.example .env
# Edit .env — add your LLM API key (OpenAI, Qwen, or MiniMax)

# Option A: Docker
docker-compose up

# Option B: Local dev
pip install -e ".[dev]"
uvicorn server.main:app --port 8000 &
cd web && npm install && npm run dev
```

Open **http://localhost:5173** and paste some corporate bullshit.

### API (30 Endpoints)

<details>
<summary><b>View all endpoints</b></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/mirror` | Full mirror analysis (translate + detect + score) |
| POST | `/api/mirror/stream` | SSE streaming analysis (progressive results) |
| POST | `/api/self-mirror` | Scan your own draft before sending |
| POST | `/api/xray` | Generate X-ray card for requirements |
| POST | `/api/deliberate` | Multi-party conflict deliberation |
| GET | `/api/reports` | List past analyses |
| GET | `/api/reports/{id}` | Get specific report |
| POST | `/api/report/weekly` | Weekly monster summary |
| GET/POST | `/api/org/config` | Organization configuration |
| GET | `/api/dashboard/summary` | Dashboard data |
| GET | `/api/dashboard/health-history` | Health score trends |
| GET | `/api/dashboard/monster-stats` | Monster frequency stats |
| CRUD | `/api/members` | Team member management |
| GET | `/api/members/{id}/patterns` | Per-person monster patterns |
| CRUD | `/api/admin/bots` | Bot connection management |
| POST | `/api/admin/bots/{id}/test` | Test bot connectivity |
| CRUD | `/api/items` | Tracked item management |
| GET | `/api/triggers/rules` | Event trigger rules |
| POST | `/api/triggers/evaluate` | Manual trigger evaluation |
| POST | `/api/bot/feishu/webhook` | Feishu bot webhook |
| POST | `/api/bot/wecom/webhook` | WeCom bot webhook |
| POST | `/api/bot/slack/events` | Slack events webhook |
| POST | `/api/bot/slack/commands` | Slack slash commands |

Interactive docs: `http://localhost:8000/docs`

</details>

### Contributing

The easiest way to contribute: **submit a new monster** via PR.

```yaml
# config/monsters/community/your_monster.yaml
id: passive_aggressive_approver
name_zh: "阴阳怪气审批妖"
name_en: "The Passive-Aggressive Approver"
category: communication
description_zh: "审批通过但措辞暗含不满"
description_en: "Approves but with undertones of displeasure"
severity_range: [1, 2]
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

### License

[MIT](LICENSE)

---

<a id="中文"></a>

## 照妖镜是什么？

一个开源 AI 框架，用来剥离组织沟通中的伪装，检测协作功能障碍模式，让模糊操作、假共识和责任漂移无处遁形。

不是项目管理工具，不是 Jira 替代品。它是组织功能障碍的 **X 光机**。

> 讽刺负责传播，诊断负责留存，建议负责价值。

### 怎么用

粘贴任何组织沟通内容（聊天记录、会议纪要、邮件），获得：

| 输出 | 功能 |
|------|------|
| **照妖翻译** | 揭示职场黑话的真实含义 |
| **妖怪检测** | 从妖怪图鉴中识别 17 种功能障碍模式 |
| **健康评分** | 4 维评估：清晰度、责任度、推进力、信任度 |
| **建议** | 认真的、可执行的建议（不讽刺） |
| **审议** | AI 代理多方冲突解决 |

### 演示

![照妖镜演示](demo_page.png)

<details>
<summary><b>示例：照妖镜照出了什么</b></summary>

**输入：**
> 张三在群里说："那个数据看板的需求，老李之前提过，我觉得方向上是对的。但现在咱们人手确实紧，小王那边还有两个紧急的要先处理。我建议我们下周拉个会，把产品、前端、数据的人都叫上，先对齐一下具体怎么做，然后再排期。"

**照妖翻译：**

| 原文 | 照妖 |
|------|------|
| "方向上是对的" | 口头支持，不代表我会做任何事 |
| "人手确实紧" | 资源否决权已激活，用"紧"当挡箭牌 |
| "下周拉个会对齐" | 会议稀释启动，用流程消耗替代推进 |

**检测到的妖怪：**
- 👻 **社交性支持妖** (Lv.2) — 口头支持但后续零资源投入
- 🧱 **资源黑洞妖** (Lv.2) — 用资源作为隐性否决权
- 🌀 **会议稀释妖** (Lv.2) — "再对齐一下"替代实际决策
- 🫥 **责任转嫁妖** (Lv.1) — 引用不在场的人转移责任

**健康评分：34/100**

</details>

### 妖怪图鉴（17 种内置模式）

<details>
<summary><b>沟通层 (6)</b></summary>

| 妖怪 | 行为 |
|------|------|
| 🦊 **评估拖延妖** | 用"评估""先看看"替代明确的是/否 |
| 👻 **社交性支持妖** | 口头支持，后续零资源投入 |
| 🎭 **模糊授权妖** | 声称有上级授权但无法追溯 |
| 🎪 **先扬后杀妖** | 先肯定再否定，无法反驳 |
| 🏔️ **大局压制妖** | 用"大局""战略"压制具体诉求 |
| 🐌 **温柔否决妖** | "我再想想" = 温柔地说不 |

</details>

<details>
<summary><b>行为层 (6)</b></summary>

| 妖怪 | 行为 |
|------|------|
| 💨 **责任扩散妖** | 无唯一 Owner，责任被稀释 |
| 🧱 **资源黑洞妖** | 口头承诺资源但从不到位 |
| 🌀 **会议稀释妖** | 用"开会对齐"替代实际推进 |
| 🐌 **Owner 幽灵妖** | 有 Owner 但此人消失了 |
| 📈 **需求膨胀防御妖** | 不断追加前置条件来否决 |
| 🫥 **责任转嫁妖** | 把责任引向不在场的人 |

</details>

<details>
<summary><b>系统层 (5)</b></summary>

| 妖怪 | 行为 |
|------|------|
| ⏰ **Deadline 漂移妖** | 截止日期悄悄后移 |
| 🔀 **层级绕行妖** | 绕过 Owner 找更高层 |
| 🧬 **需求变异妖** | 需求在执行中被悄悄改写 |
| 🏚️ **技术债甩锅妖** | "历史遗留" = 永久豁免 |
| 🎣 **信息武器化妖** | 选择性不共享关键信息 |

</details>

### 五种触发模式

```
 自然程度
    ↑
    │  ⑤ 全自动：所有事项默认过镜（最自然）
    │  ④ 事件触发：满足条件时自动过镜
    │  ③ 自扫模式：扫描自己的话（中性）
    │  ② @Bot：有人在群里主动触发（稍刻意）
    │  ① 手动粘贴：复制文本到网页（最刻意）
    └──────────────────────────────────────────▶ 接入成本
```

### 快速开始

```bash
git clone https://github.com/your-org/zhaoyaojing.git
cd zhaoyaojing

cp .env.example .env
# 编辑 .env — 填入你的 LLM API Key（OpenAI / 通义千问 / MiniMax）

# 方式 A: Docker
docker-compose up

# 方式 B: 本地开发
pip install -e ".[dev]"
uvicorn server.main:app --port 8000 &
cd web && npm install && npm run dev
```

打开 **http://localhost:5173**，粘贴一段职场废话试试。

### 贡献

最简单的贡献方式：**提交一个新妖怪** (PR)。

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

### 更多文档

- [设计文档](ZhaoYaoJing-Design.md) — 完整架构设计（1499 行）
- [部署指南](docs/DEPLOYMENT.md) — VPS / Railway / 本地 + ngrok
- [Bot 接入指南](docs/BOT_SETUP_GUIDE.md) — 飞书 / 企微 / Slack 配置
- [API 文档](http://localhost:8000/docs) — Swagger UI（30 个端点）

### 许可证

[MIT](LICENSE)
