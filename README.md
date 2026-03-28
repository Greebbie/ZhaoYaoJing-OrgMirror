<div align="center">

# 照妖镜 ZhaoYaoJing — OrgMirror

### 把办公室里的妖魔鬼怪照出原形。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)

**[English](README_EN.md)** | **中文**

</div>

---

## 这是什么？

一个开源 AI 框架——剥离组织沟通中的伪装，检测协作功能障碍模式，让模糊操作、假共识和责任漂移无处遁形。

不是项目管理工具，不是 Jira 替代品。它是组织功能障碍的 **X 光机**。

> **讽刺负责传播，诊断负责留存，建议负责价值。**

---

## 演示

![照妖镜演示](demo_page.png)

<details>
<summary><b>完整示例：照妖镜照出了什么</b></summary>

**输入：**
> 张三在群里说："那个数据看板的需求，老李之前提过，我觉得方向上是对的。但现在咱们人手确实紧，小王那边还有两个紧急的要先处理。我建议我们下周拉个会，把产品、前端、数据的人都叫上，先对齐一下具体怎么做，然后再排期。"

**照妖翻译：**

| 原文 | 照妖 |
|------|------|
| "方向上是对的" | 口头支持，不代表我会做任何事 |
| "人手确实紧" | 资源否决权已激活，用"紧"当挡箭牌 |
| "下周拉个会对齐" | 会议稀释启动，用流程消耗替代推进 |
| "老李之前提过" | 不是我提的，出了问题跟我没关系 |

**检测到的妖怪：**
- 👻 **社交性支持妖** (Lv.2) — 口头支持但后续零资源投入
- 🧱 **资源黑洞妖** (Lv.2) — 用资源作为隐性否决权
- 🌀 **会议稀释妖** (Lv.2) — "再对齐一下"替代实际决策
- 🫥 **责任转嫁妖** (Lv.1) — 引用不在场的人转移责任

**健康评分：34/100** (清晰度 35 | 责任度 25 | 推进力 32 | 信任度 42)

**建议：**
1. [HIGH] 追问具体负责人：当对方说"方向上是对的"时，立即追问"那谁来做？谁是 owner？"
2. [HIGH] 量化资源缺口：当对方说"人手紧"时，追问"需要多少人？什么时候能到位？"
3. [HIGH] 要求会前输出：同意"下周开会"之前，要求对方先发一份方案初稿

</details>

---

## 怎么用

粘贴任何组织沟通内容（聊天记录、会议纪要、邮件），获得：

| 输出 | 功能 |
|------|------|
| 🪞 **照妖翻译** | 揭示职场黑话的真实含义 |
| 👻 **妖怪检测** | 从妖怪图鉴中识别 17 种功能障碍模式 |
| 📊 **健康评分** | 4 维评估：清晰度、责任度、推进力、信任度 |
| 💡 **建议** | 认真的、可执行的建议（不讽刺） |
| ⚖️ **审议** | AI 代理多方冲突解决 |

---

## 妖怪图鉴（17 种内置模式）

<details>
<summary><b>沟通层 (6 种)</b></summary>

| 妖怪 | 行为 |
|------|------|
| 🦊 **评估拖延妖** | 用"评估""先看看"替代明确的是/否 |
| 👻 **社交性支持妖** | 口头支持，后续零资源投入 |
| 🎭 **模糊授权妖** | 声称有上级授权但无法追溯 |
| 🎪 **先扬后杀妖** | 先肯定再否定，让人无法反驳 |
| 🏔️ **大局压制妖** | 用"大局""战略"压制具体诉求 |
| 🐌 **温柔否决妖** | "我再想想" = 温柔地说不 |

</details>

<details>
<summary><b>行为层 (6 种)</b></summary>

| 妖怪 | 行为 |
|------|------|
| 💨 **责任扩散妖** | 无唯一 Owner，责任被集体稀释 |
| 🧱 **资源黑洞妖** | 口头承诺资源但从不到位 |
| 🌀 **会议稀释妖** | 用"开会对齐"替代实际推进 |
| 🐌 **Owner 幽灵妖** | 有 Owner 但此人消失了 |
| 📈 **需求膨胀防御妖** | 不断追加前置条件来实质否决 |
| 🫥 **责任转嫁妖** | 把责任引向不在场的人 |

</details>

<details>
<summary><b>系统层 (5 种)</b></summary>

| 妖怪 | 行为 |
|------|------|
| ⏰ **Deadline 漂移妖** | 截止日期悄悄后移，无正式宣布 |
| 🔀 **层级绕行妖** | 绕过 Owner 直接找更高层 |
| 🧬 **需求变异妖** | 需求在执行中被悄悄改写 |
| 🏚️ **技术债甩锅妖** | "历史遗留" = 永久豁免现在的不作为 |
| 🎣 **信息武器化妖** | 选择性不共享关键信息制造信息差 |

</details>

---

## 五种触发模式

```
 自然程度
    ↑
    │  ⑤ 全自动：所有事项默认过镜（最自然，像基础设施）
    │  ④ 事件触发：满足条件时自动过镜（像 CI/CD）
    │  ③ 自扫模式：发消息前先照自己（无攻击性，自省）
    │  ② @Bot：群里 @照妖镜 分析讨论（取决于用法）
    │  ① 手动粘贴：复制文本到网页扫描（最刻意，像告状）
    └───────────────────────────────────────────▶ 接入成本
```

**关键创新：自扫模式（Mode ③）**——发消息之前先过照妖镜检查自己是不是在含糊其辞。从"我在扫你"变成"我在照自己"。

---

## 快速开始

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

---

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python 3.11+ / FastAPI / SQLAlchemy |
| 前端 | React 19 / TypeScript / Vite |
| 数据库 | SQLite (开发) / PostgreSQL (生产) |
| 模型 | OpenAI / 通义千问 / Gemini / MiniMax（多模型自动切换） |
| Bot | 飞书 / 企业微信 / Slack |
| 部署 | Docker Compose |

---

## API（30 个端点）

<details>
<summary><b>查看全部端点</b></summary>

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/mirror` | 完整照妖分析 |
| POST | `/api/mirror/stream` | SSE 流式分析（逐步返回结果） |
| POST | `/api/self-mirror` | 自扫模式 |
| POST | `/api/xray` | X 光片生成 |
| POST | `/api/deliberate` | 多方审议 |
| GET | `/api/reports` | 历史报告列表 |
| GET | `/api/reports/{id}` | 报告详情 |
| POST | `/api/report/weekly` | 周报统计 |
| GET/POST | `/api/org/config` | 组织配置 |
| GET | `/api/dashboard/summary` | 仪表盘数据 |
| GET | `/api/dashboard/health-history` | 健康趋势 |
| GET | `/api/dashboard/monster-stats` | 妖怪统计 |
| CRUD | `/api/members` | 团队成员管理 |
| GET | `/api/members/{id}/patterns` | 成员妖怪模式 |
| CRUD | `/api/admin/bots` | Bot 接入管理 |
| POST | `/api/admin/bots/{id}/test` | 测试 Bot 连接 |
| CRUD | `/api/items` | 事项跟踪 |
| GET | `/api/triggers/rules` | 触发规则 |
| POST | `/api/triggers/evaluate` | 手动触发评估 |
| POST | `/api/bot/feishu/webhook` | 飞书 webhook |
| POST | `/api/bot/wecom/webhook` | 企微 webhook |
| POST | `/api/bot/slack/events` | Slack webhook |

交互文档：`http://localhost:8000/docs`

</details>

---

## 贡献

最简单的贡献方式：**提交一个新妖怪**。

```yaml
# config/monsters/community/your_monster.yaml
id: passive_aggressive_approver
name_zh: "阴阳怪气审批妖"
name_en: "The Passive-Aggressive Approver"
category: communication
description_zh: "审批通过但措辞暗含不满，让被审批者赢了但不敢开心"
description_en: "Approves but with undertones of displeasure"
severity_range: [1, 2]
contributed_by: "your_github_username"
```

详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

---

## 更多文档

- [设计文档](ZhaoYaoJing-Design.md) — 完整架构设计
- [部署指南](docs/DEPLOYMENT.md) — VPS / Railway / 本地部署
- [Bot 接入指南](docs/BOT_SETUP_GUIDE.md) — 飞书 / 企微 / Slack 配置

---

## 许可证

[MIT](LICENSE)
