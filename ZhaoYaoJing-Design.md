# 照妖镜 ZhaoYaoJing — OrgMirror

> **把办公室里的妖魔鬼怪照出原形。**
> **Strip the bullshit. See the real org.**

An open-source AI framework that strips away organizational bullshit, detects collaboration dysfunction patterns, and makes it structurally harder for people to hide behind vague language, fake consensus, and accountability drift.

Not a project management tool. Not a Jira replacement. It's an X-ray machine for organizational dysfunction.

**开源组织透视框架** — 用 AI 剥离组织沟通中的伪装，检测协作功能障碍模式，让模糊操作、假共识和责任漂移无处遁形。

---

## Table of Contents

- [Why This Exists / 为什么需要这个](#why-this-exists)
- [Core Design Philosophy / 核心设计哲学](#core-design-philosophy)
- [Trigger Mechanism Design / 触发机制设计](#trigger-mechanism-design)
- [System Architecture / 系统架构](#system-architecture)
- [Monster Codex / 妖怪图鉴](#monster-codex)
- [Agent System / Agent 系统](#agent-system)
- [LLM Backend / 模型后端](#llm-backend)
- [Bot Integration / Bot 接入](#bot-integration)
- [Fool-proof Setup / 傻瓜化配置](#fool-proof-setup)
- [Identity & Org Info / 身份与组织信息](#identity-and-org-info)
- [Input/Output Schema / 输入输出 Schema](#input-output-schema)
- [Tech Stack & Project Structure / 技术栈与项目结构](#tech-stack-and-project-structure)
- [Demo Case / 示例](#demo-case)
- [Community / 开源社区](#community)
- [FAQ](#faq)

---

<a id="why-this-exists"></a>
## Why This Exists / 为什么需要这个

Every organization — whether a 3-person startup or a 10,000-person enterprise — runs on a hidden operating system:

每个组织都有一套隐性操作系统：

- Requirements aren't rejected; they're "evaluated" to death
  需求不是被拒绝的，是被「再评估一下」拖死的
- Responsibility isn't dodged; it's "collectively owned" into oblivion
  责任不是被推掉的，是被「大家一起负责」稀释掉的
- Direction isn't opposed; it's "aligned" into ambiguity
  方向不是被否定的，是被「我们先对齐一下」模糊掉的
- Progress isn't blocked; it's "resource-constrained" indefinitely
  进度不是被阻塞的，是被「资源比较紧张」无限期搁置的

**These tactics work not because no one notices, but because they're wrapped in a layer of professional language.**

**这些操作之所以有效，不是因为没人看见，而是因为它们被精心包装在一层"专业措辞"里。**

ZhaoYaoJing does one thing: **strip that wrapping off.**

照妖镜做一件事：**把这层包装撕掉。**

---

<a id="core-design-philosophy"></a>
## Core Design Philosophy / 核心设计哲学

### Not Another App People "Go To" / 不是又一个要人「去用」的 App

The problem with Jira, Feishu, Notion isn't lack of features — **it's that the people who need management the most are the least likely to use management tools properly.** You can't expect someone who profits from ambiguity to voluntarily write things clearly.

Jira、飞书、Notion 的问题不是功能不够——**最需要被管理的人，恰恰是最不会好好用管理工具的人。**

ZhaoYaoJing is not a destination. It's a **transparency layer** that sits on top of existing communication.

照妖镜不是一个目的地，而是一层架在现有沟通之上的**透视层**。

### Satire is the Trojan Horse / 讽刺是特洛伊木马

No org will formally adopt an "Organizational Transparency Framework" — the name alone would be politically assassinated. But people will try "ZhaoYaoJing" because it's fun, discover "holy shit this IS our team", and then start reading the serious recommendations.

没有任何组织会正式引入一个叫 "组织透明化框架" 的东西。但「照妖镜」不一样——人们会因为好玩去试。

**Satire drives adoption. Diagnosis drives retention. Recommendations drive value.**

**讽刺负责传播，诊断负责留存，建议负责价值。**

---

<a id="trigger-mechanism-design"></a>
## Trigger Mechanism Design / 触发机制设计

**This is the most critical design decision in the entire project.**

**这是整个项目最关键的设计决策。**

### The Core Problem / 核心问题

If someone manually copies a colleague's message into a scanner, that's not analysis — that's an accusation. The social dynamics are toxic from the start.

如果有人手动复制同事的话去网页扫描，那不是分析——那是告状。社交动态从一开始就是有毒的。

But if the mirror activates **naturally as part of the workflow**, it's infrastructure, not a weapon.

但如果照妖镜作为**工作流程的自然组成部分**被触发，它就是基础设施，不是武器。

**Rule: The mirror should never feel like "I'm scanning YOU." It should feel like "this SITUATION is being scanned."**

**原则：照妖镜永远不应该让人觉得「我在扫描你」，而应该让人觉得「这个事情在被扫描」。**

### Five Trigger Modes / 五种触发模式

```
 自然程度
    ↑
    │  ⑤ 全自动：所有事项自动过镜（最自然）
    │  ④ 事件触发：满足条件时自动过镜
    │  ③ 自扫模式：扫描自己的话（中性）
    │  ② @Bot：有人在群里主动触发（稍刻意）
    │  ① 手动粘贴：复制别人的话去网页（最刻意，最像告状）
    └──────────────────────────────────▶ 接入成本
```

---

### Mode ① 手动粘贴 — Web Portal / Manual Paste

```
使用方式：打开网页 → 粘贴文本 → 获得报告
触发者：个人
可见性：仅自己
社交感受：⚠️ 像在背后告状
```

**When it works**: Personal use, retrospective analysis, "is it just me or is something off" sanity checks.

**适用场景**：个人使用、复盘分析、「是不是就我觉得不对劲」的理性检查。

**Design guardrail**: Web portal output ALWAYS defaults to anonymized mode. No names, only Role A / Role B. This reduces the "gotcha" feeling even when sharing results.

**设计护栏**：Web 端输出**始终默认匿名模式**。不显示名字，只显示角色 A / 角色 B。即使分享结果也不那么像针对谁。

---

### Mode ② @Bot 主动触发 — Bot Mention in Chat

```
使用方式：在群里 @照妖镜 + 引用某段讨论
触发者：任何群成员
可见性：全群可见
社交感受：⚡ 取决于怎么用
```

**This is a double-edged sword.** If someone @mirrors a specific person's message, it still feels targeted.

**这是双刃剑。** 如果有人 @照妖镜 指向某个人的消息，依然会感觉有针对性。

**Design solution: @Bot analyzes the ENTIRE discussion thread, not a single message.**

**设计方案：@Bot 分析的是整段讨论，而不是单条消息。**

```
✗ BAD:  回复张三的消息 → @照妖镜
        （感觉：我在针对张三）

✓ GOOD: @照妖镜 帮我们看看这个需求讨论有没有卡点
        （感觉：我们一起看看事情推不推得动）
```

When @Bot is triggered, it:
1. Grabs the recent N messages in the thread (not a single message)
2. Analyzes the whole discussion
3. Outputs a neutral, situation-focused report
4. Never singles out individuals unless the report is anonymized

@Bot 被触发时：
1. 抓取当前讨论的最近 N 条消息（不是单条消息）
2. 分析整个讨论
3. 输出中性的、聚焦事项的报告
4. 除非匿名化，否则不点名

**Additional @Bot commands:**

```
@照妖镜 扫描            → 扫描最近 30 条群消息
@照妖镜 事项 [描述]      → 将描述转为事项 X 光片
@照妖镜 复盘 [事项名]    → 拉取该事项历史，生成尸检报告
@照妖镜 周报            → 手动触发本周妖气报告
@照妖镜 自查            → 私聊返回：扫描你自己最近的发言
```

---

### Mode ③ Self-Mirror / 照照自己 — 自扫模式

**This is the mode that flips the social dynamics entirely.**

**这是彻底翻转社交动态的模式。**

```
使用方式：你把自己要发的内容先过一遍照妖镜
触发者：自己
可见性：仅自己
社交感受：✅ 完全无攻击性，反而体现自省
```

**How it works**: Before you send a message in a group, you pass it through the mirror to check:
- Am I being vague?
- Am I accidentally doing a "phantom support"?
- Is my statement actually actionable or just noise?

**工作方式**：在你发群消息之前，先过照妖镜检查：
- 我是不是在含糊其辞？
- 我是不是在做「社交性支持」？
- 我说的话是否有可执行性？

```
┌─────────────────────────────────────────────┐
│  🪞 自扫模式                                  │
│                                              │
│  你准备发送:                                   │
│  「这个方向我支持，但资源上我们再看看」           │
│                                              │
│  照妖镜提醒:                                   │
│  ⚠️ 检测到 👻社交性支持 + 🧱资源黑洞            │
│  你在口头支持但没给具体承诺。                    │
│                                              │
│  建议改为:                                     │
│  「我支持这个方向。资源方面，我这边最快能在       │
│   4/15 之后排出一个人，需要大概两周时间。         │
│   如果要提前，需要把 XX 项目暂停。」             │
│                                              │
│  [直接发送原文]  [用建议版本]  [自己改]          │
└─────────────────────────────────────────────┘
```

**This is powerful because:**
- It makes the mirror a **writing assistant**, not a surveillance tool
- People voluntarily improve their communication
- Over time, the entire org's communication quality goes up
- Nobody feels accused — you're accusing yourself

**这很强大因为：**
- 照妖镜变成了**写作助手**，而不是监控工具
- 人们主动改善自己的沟通
- 长期来看，整个组织的沟通质量提升
- 没人觉得被针对——你是在照自己

---

### Mode ④ Event-Triggered / 事件触发 — 满足条件自动过镜

```
使用方式：当满足特定条件时，照妖镜自动扫描并推送
触发者：系统
可见性：可配置（推给相关人 / 推给群 / 推给 manager）
社交感受：✅ 中性，是系统行为
```

**Trigger conditions (configurable):**

**触发条件（可配置）：**

```yaml
triggers:
  # 需求/事项相关
  - type: new_requirement
    desc: "有人提出新需求/事项时，自动生成 X 光片"
    action: generate_xray
    visibility: thread  # 在同一讨论串回复

  # 时间相关
  - type: stale_item
    desc: "事项超过 N 天无更新"
    condition: "days_since_last_update > 7"
    action: generate_blocker_report
    visibility: owner + stakeholders

  # 模式相关
  - type: meeting_repeat
    desc: "同一议题第 3 次出现在会议中"
    action: flag_meeting_vortex
    visibility: thread

  # 承诺相关
  - type: commitment_no_followup
    desc: "有人说了「我来做」但 72h 无后续动作"
    action: gentle_reminder
    visibility: private_to_person

  # owner 相关
  - type: owner_silence
    desc: "事项 owner 超过 5 天未在相关讨论中发言"
    action: flag_ghost_owner
    visibility: owner + thread

  # 自定义
  - type: custom
    desc: "用户自定义规则"
    condition: "..."
    action: "..."
```

**Key insight: event triggers feel like CI/CD, not surveillance.** Just like linting catches code smells automatically, ZhaoYaoJing catches org smells automatically. Nobody thinks the linter is "targeting" them.

**关键洞察：事件触发感觉像 CI/CD，而不是监控。** 就像 linter 自动检查代码异味，照妖镜自动检查组织异味。没人会觉得 linter 在「针对」自己。

---

### Mode ⑤ Always-On / 全自动 — 所有事项默认过镜

```
使用方式：照妖镜持续监听团队沟通渠道，自动分析
触发者：系统
可见性：Dashboard + 周报
社交感受：✅ 完全是基础设施
```

**This is the ultimate form** — ZhaoYaoJing runs as background infrastructure, like an APM for organizational health.

**这是终极形态** — 照妖镜作为后台基础设施运行，就像组织健康的 APM。

```
┌──────────────────────────────────────────────────────┐
│  ZhaoYaoJing Dashboard                                │
│                                                       │
│  组织健康分: 64/100  (↓3 vs 上周)                      │
│                                                       │
│  本周妖气排行:                                         │
│  1. 👻 社交性支持妖  ████████████░░  出现 12 次        │
│  2. 🌀 会议稀释妖    ██████████░░░░  出现 9 次         │
│  3. 💨 责任扩散妖    ████████░░░░░░  出现 7 次         │
│                                                       │
│  高危事项:                                             │
│  🔴 数据看板需求 — 14 天无 owner，3 次会议无结论        │
│  🟡 API 重构 — deadline 已漂移 2 次                    │
│  🟡 客户 Demo — 口头支持 4 人，实际推进 0 人            │
│                                                       │
│  模式警报:                                             │
│  ⚠️ 张三在过去 30 天内触发 👻社交性支持 8 次             │
│  ⚠️「对齐会」在过去 2 周被提议 6 次，产出结论 0 次       │
└──────────────────────────────────────────────────────┘
```

### Recommended Rollout Strategy / 建议的推出策略

**Don't start with Mode ⑤.** Start with the modes that feel least threatening:

**不要一上来就搞全自动。** 从最不具威胁性的模式开始：

```
Phase 1: Mode ③ Self-Mirror + Mode ① Web Portal
         让人先「照自己」，建立信任
         ↓
Phase 2: Mode ② @Bot in groups
         团队开始自然地在讨论中使用
         ↓
Phase 3: Mode ④ Event triggers
         自动化规则，变成基础设施
         ↓
Phase 4: Mode ⑤ Always-on dashboard
         全自动，组织级别的健康监控
```

---

<a id="system-architecture"></a>
## System Architecture / 系统架构

### High-Level / 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      INPUT LAYER                             │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Web UI   │  │ Feishu   │  │ WeCom    │  │ Slack    │    │
│  │ Portal   │  │ Bot      │  │ Bot      │  │ Bot      │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       └──────────────┴──────────────┴──────────────┘         │
│                          │                                   │
│                    Unified Input API                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     CORE ENGINE                              │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐    │
│  │ Intake      │  │ Mirror      │  │ Monster          │    │
│  │ Parser      │  │ Translator  │  │ Detector         │    │
│  │ 输入解析     │  │ 照妖翻译    │  │ 妖怪检测          │    │
│  └──────┬──────┘  └──────┬──────┘  └────────┬─────────┘    │
│         └────────────────┼──────────────────┘               │
│                          │                                   │
│  ┌─────────────┐  ┌─────┴───────┐  ┌──────────────────┐    │
│  │ X-Ray       │  │ Agent       │  │ Health           │    │
│  │ Generator   │  │ Deliberation│  │ Scorer           │    │
│  │ X光片生成   │  │ Agent 审议  │  │ 健康评分          │    │
│  └─────────────┘  └─────────────┘  └──────────────────┘    │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LLM Router (multi-backend)                │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────────┐ │  │
│  │  │ OpenAI │ │ Qwen   │ │ Gemini │ │ MiniMax        │ │  │
│  │  └────────┘ └────────┘ └────────┘ └────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    PERSISTENCE LAYER                         │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ Item     │  │ Pattern      │  │ Org Config         │    │
│  │ Store    │  │ Memory       │  │ Store              │    │
│  │ 事项存储  │  │ 模式记忆      │  │ 组织配置存储        │    │
│  └──────────┘  └──────────────┘  └────────────────────┘    │
│                                                              │
│                      SQLite / PostgreSQL                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     OUTPUT LAYER                             │
│                                                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐               │
│  │ Web UI    │  │ Bot Reply │  │ Dashboard │               │
│  │ Reports   │  │ 群消息回复  │  │ 仪表盘    │               │
│  └───────────┘  └───────────┘  └───────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

<a id="monster-codex"></a>
## Monster Codex / 妖怪图鉴

The Monster Codex is the project's **core IP and content asset**. Each organizational dysfunction pattern is a named, detectable "monster."

妖怪图鉴是项目的**核心 IP 和内容资产**。每种组织功能障碍模式都是一个命名的、可检测的「妖怪」。

### Severity Levels / 严重度评级

| Level | Mark | Meaning (EN) | 含义 |
|-------|------|--------------|------|
| Lv.1 | 🟢 小妖 | Minor — happens occasionally, human nature | 偶尔发生，属于人之常情，提醒即可 |
| Lv.2 | 🟡 老妖 | Established — habitual pattern, eroding trust | 已成习惯性模式，正在消耗团队信任 |
| Lv.3 | 🔴 妖王 | Critical — systemic, dragging down core collaboration | 系统性病灶，正在拖垮核心协作 |
| Lv.4 | 💀 尸变 | Terminal — org is functionally dead, just still having meetings | 组织已经功能性死亡，只是还在开会 |

---

### Communication Layer Monsters / 沟通层妖怪

#### 🦊 评估拖延妖 The Eternal Evaluator

- **Symptom**: Uses "evaluate" / "research" / "let's see" to replace clear yes/no
- **症状**：用「评估」「调研」「先看看」替代明确的是/否
- **Detection**: Same item hits "let's evaluate" ≥ 2 times with no evaluation output
- **检测信号**：同一事项出现 2 次以上「先评估」且无评估产出物
- **Mechanism**: Substitutes procedural illusion for actual decision-making
- **真实机制**：用流程幻觉替代决策
- **Classic line**: "Let's first evaluate the feasibility on this"
- **经典台词**：「这个我们先评估一下可行性」

#### 👻 社交性支持妖 The Phantom Ally

- **Symptom**: Verbally supports but follows up with zero resources or actions
- **症状**：口头表态支持，但后续无任何资源投入或动作
- **Detection**: Person states "support/agree" then has no associated action within 30 days
- **检测信号**：某人表态「支持/同意」后，30 天内无关联动作记录
- **Mechanism**: Trades low-cost verbal commitment for social goodwill while preserving exit
- **真实机制**：用低成本的语言承诺换取社交好感，同时保留退出路径
- **Classic line**: "Directionally I'm very supportive"
- **经典台词**：「方向上我是非常支持的」

#### 🎭 模糊授权妖 The Ghost Mandate

- **Symptom**: Claims upper-level authorization that can't be traced to specific person/time/scope
- **症状**：声称有上级授权，但无法追溯具体人、具体时间、具体条件
- **Detection**: Appears "leadership said" / "word from above" without meeting notes/email/doc evidence
- **检测信号**：出现「领导说」「上面的意思」但无会议纪要/邮件/文档佐证
- **Mechanism**: Leverages phantom authority to push personal agenda
- **真实机制**：借用权力幻影推进个人意图
- **Classic line**: "The boss mentioned this before"
- **经典台词**：「这个老板之前提过的」

#### 🎪 先扬后杀妖 The Compliment Assassin

- **Symptom**: Affirm first then negate, making direct rebuttal impossible
- **症状**：先肯定再否定，让人无法直接反驳
- **Detection**: "You're right / good idea / definitely a direction" followed immediately by "but / however / just that"
- **检测信号**：「你说得对/想法挺好/确实是个方向」后紧跟「但是/不过/只是」
- **Mechanism**: Wraps veto in politeness, making opposition unchallengeable
- **真实机制**：用礼貌包装否决权，使反对变得不可挑战
- **Classic line**: "Great thinking, but not quite right for this stage"
- **经典台词**：「你这个思路很好，但目前阶段可能不太适合」

#### 🏔️ 大局压制妖 The Big Picture Bully

- **Symptom**: Uses "big picture" / "strategy" / "long-term" to suppress specific legitimate needs
- **症状**：用「大局」「战略」「长远」来压制具体的合理诉求
- **Detection**: In resource/priority disputes, one party uses abstract framing to deny another's concrete request
- **检测信号**：在资源/优先级争夺中，一方使用抽象框架否定另一方的具体需求
- **Mechanism**: Disguises interest conflict as vision gap
- **真实机制**：把利益冲突伪装成格局差异
- **Classic line**: "You need to see the big picture, not just your piece"
- **经典台词**：「你要有大局观，不能只看自己这块」

#### 🐌 温柔否决妖 The Gentle Vetoist

- **Symptom**: Expresses disagreement as "let me think about it" / "we could consider" instead of clear no
- **症状**：用「我再想想」「可以考虑」替代明确的反对
- **Detection**: Soft language patterns followed by no action or quiet topic-change
- **检测信号**：柔性表达后无后续动作或悄悄转移话题
- **Classic line**: "I think this could use more thought"
- **经典台词**：「我觉得这个事情可以再想想」

---

### Behavior Layer Monsters / 行为层妖怪

#### 💨 责任扩散妖 The Diffusion Ghost

- **Symptom**: No single owner, or owner changes repeatedly
- **症状**：事项无唯一 Owner，或 Owner 频繁变更
- **Detection**: Item owner field empty / multi-person / changed ≥ 2 times
- **检测信号**：事项记录中 owner 字段为空/为多人/变更 ≥ 2 次
- **Mechanism**: Collective responsibility dilutes individual accountability
- **真实机制**：用集体责任稀释个人问责
- **Classic line**: "Let's all push on this together"
- **经典台词**：「这个事情大家一起推一下」

#### 🧱 资源黑洞妖 The Resource Void

- **Symptom**: Verbal resource commitment but actual delivery never materializes
- **症状**：口头承诺资源但实际从不到位
- **Detection**: Party mentions "tight resources" multiple times without specific scheduling or alternatives
- **检测信号**：某方多次在讨论中提到「资源紧张」但从未给出具体排期或替代方案
- **Mechanism**: Uses resources as implicit veto power
- **真实机制**：用资源作为隐性否决权
- **Classic line**: "We're really stretched thin, let me see what I can do"
- **经典台词**：「人手确实比较紧，我看看怎么调配」

#### 🌀 会议稀释妖 The Meeting Vortex

- **Symptom**: Substitutes "let's schedule a sync" for actual progress
- **症状**：用「再开个会对齐」替代实际推进
- **Detection**: Same topic appears in ≥ 3 meetings with no new conclusion
- **检测信号**：同一议题在 3 次以上会议中出现，无新结论
- **Mechanism**: Process consumption replaces substantive progress
- **真实机制**：用流程消耗替代实质进展
- **Classic line**: "Let's set up a meeting to align on this"
- **经典台词**：「这个我们约个会再对齐一下」

#### 🐌 Owner 幽灵妖 The Ghost Owner

- **Symptom**: Named owner but person effectively vanishes
- **症状**：名义上有 Owner，但此人实际消失、不推进、不回应
- **Detection**: Owner absent from last N rounds of discussion/follow-up
- **检测信号**：Owner 在最近 N 轮讨论/跟进中无发言或动作
- **Mechanism**: Holds position without doing work, neither releasing nor progressing
- **真实机制**：占位不做事，既不放手也不推进
- **Classic line**: (silence)
- **经典台词**：（沉默）

#### 📈 需求膨胀防御妖 The Scope Creep Shield

- **Symptom**: Continuously adds prerequisites to effectively kill an initiative
- **症状**：通过不断追加前置条件/要求来实质否决一件事
- **Detection**: Same item's scope/prerequisites grow across ≥ 3 rounds of communication
- **检测信号**：同一事项的 scope/前置条件在 3 轮沟通中持续增加
- **Mechanism**: Uses "thoroughness" to ensure nothing ever starts
- **真实机制**：用「完善」的名义让事情永远无法启动
- **Classic line**: "If we're doing this, we should also factor in XX"
- **经典台词**：「要做的话，那我们还得先把XX也考虑进去」

#### 🫥 责任转嫁妖 The Blame Redirector

- **Symptom**: Attributes responsibility to absent or uninvolved parties
- **症状**：把责任引向不在场的人或不相关的人
- **Detection**: References absent person as original owner/initiator
- **检测信号**：在讨论中引用不在场的人作为事项发起者或负责方
- **Classic line**: "Wasn't XX looking at this?"
- **经典台词**：「这个之前不是XX在看吗？」

---

### Structural Layer Monsters / 系统层妖怪

#### ⏰ Deadline 漂移妖 The Sliding Deadline

- **Symptom**: Deadline quietly shifts backward without formal announcement
- **症状**：截止日期悄悄后移，无正式宣布、无原因记录
- **Detection**: Same item's time anchor retreats ≥ 2 times across communications
- **检测信号**：同一事项的时间锚点在多轮沟通中后退 ≥ 2 次
- **Mechanism**: Micro-adjustments avoid formal "delay" classification
- **真实机制**：用微调避免正式的「延期」定性
- **Classic line**: "Should be ready next week... (next week) let's see"
- **经典台词**：「下周应该可以，（下周）再看看吧」

#### 🔀 层级绕行妖 The Bypass Artist

- **Symptom**: Goes around direct owner to higher authority or alternative paths
- **症状**：绕过直接 Owner/负责人，直接找更高层或其他路径推动
- **Detection**: Non-directly-related senior leader appears in decision chain
- **检测信号**：决策链中出现非直接相关的高层介入
- **Mechanism**: Exploits information asymmetry and power differential to create fait accompli
- **真实机制**：利用信息不对称和权力差制造既成事实
- **Classic line**: "I chatted with VP XX, he thinks it's fine"
- **经典台词**：「我跟XX总聊了一下，他觉得可以」

#### 🧬 需求变异妖 The Mutation Drift

- **Symptom**: Requirements/goals/acceptance criteria quietly rewritten during execution
- **症状**：需求、目标、验收标准在执行过程中被悄悄改写
- **Detection**: Item's core definition (goal/scope/success criteria) inconsistent across documents/discussions
- **检测信号**：事项的核心定义在不同文档/讨论中不一致
- **Mechanism**: Controls the narrative by redefining reality
- **真实机制**：通过重新定义来掌控叙事权
- **Classic line**: "That's not what we originally meant, right?"
- **经典台词**：「我们最开始说的不是这个意思吧？」

#### 🏚️ 技术债甩锅妖 The Legacy Blame

- **Symptom**: All problems attributed to "historical reasons" with no one taking ownership
- **症状**：所有问题归因于「历史遗留」，无人接手改善
- **Detection**: Same "legacy issue" mentioned ≥ 3 times with no solution output
- **检测信号**：同一「历史遗留」问题被提及 ≥ 3 次，无解决方案产出
- **Mechanism**: Uses past chaos to permanently exempt present inaction
- **真实机制**：用过去的混乱为现在的不作为提供永久豁免
- **Classic line**: "That's a legacy issue, nothing we can do"
- **经典台词**：「这个是历史遗留问题，没办法」

#### 🎣 信息武器化妖 The Info Gatekeeper

- **Symptom**: Selectively withholds information to maintain power asymmetry
- **症状**：选择性地不共享关键信息，制造信息差
- **Detection**: Decision-relevant information only circulates among subset of stakeholders
- **检测信号**：决策相关信息仅在部分人之间流通
- **Classic line**: "Oh, you didn't know? I thought someone told you"
- **经典台词**：「啊你不知道吗？我以为有人跟你说了」

---

<a id="agent-system"></a>
## Agent System / Agent 系统

### Why Agents from Day One / 为什么从第一天就需要 Agent

A single LLM call can do translation and detection. But the real value — structural analysis, multi-perspective reasoning, pattern tracking — needs agents.

单次 LLM 调用能做翻译和检测。但真正的价值——结构化分析、多视角推理、模式追踪——需要 Agent。

### Agent Roster / Agent 清单

```
┌─────────────────────────────────────────────────────────────┐
│                    CORE AGENTS (v1)                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📥 Intake Agent (收件妖)                                    │
│     Converts any input (chat, meeting notes, email)          │
│     into structured item cards                               │
│     把任何输入转成标准事项卡                                    │
│                                                              │
│  🔍 Clarification Agent (挑刺妖)                             │
│     Checks for missing information, lists mandatory          │
│     questions. Incomplete = doesn't proceed                  │
│     检查缺失信息，不完整就不往后走                              │
│                                                              │
│  🪞 Mirror Agent (照妖主镜)                                   │
│     Core translation + monster detection engine              │
│     核心照妖翻译 + 妖怪检测引擎                                │
│                                                              │
│  📊 Health Agent (体检妖)                                     │
│     Calculates org health score across dimensions            │
│     计算组织多维健康分数                                       │
│                                                              │
│  💡 Advisor Agent (军师妖)                                    │
│     Generates actionable, non-sarcastic recommendations      │
│     生成可执行的、认真的建议（不讽刺）                          │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                DELIBERATION AGENTS (v1)                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🎭 Advocate Agent × N (代言妖)                               │
│     One per stakeholder party. Represents their              │
│     constraints, preferences, and red lines                  │
│     每个利益方一个，代表其约束、偏好和底线                       │
│                                                              │
│  ⚖️  Arbiter Agent (仲裁妖)                                   │
│     NOT a judge — a convergence engine.                      │
│     Synthesizes all input into option packages               │
│     不是裁判——是收敛引擎。综合所有输入产出方案包                 │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                MEMORY AGENTS (v1)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🧠 Memory Agent (记忆妖)                                    │
│     Tracks historical patterns, identifies recurring         │
│     dysfunction across items and time                        │
│     追踪历史模式，跨事项跨时间识别反复出现的问题                  │
│                                                              │
│  🔄 Drift Agent (漂移妖)                                     │
│     Detects silent changes to requirements, owners,          │
│     goals, and deadlines                                     │
│     检测需求/owner/目标/deadline 的悄悄改写                    │
│                                                              │
│  🚨 Escalation Agent (升级妖)                                 │
│     When items stall beyond threshold, generates             │
│     objective escalation summaries                           │
│     长期不推进时，自动生成客观升级摘要                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Agent Orchestration / Agent 编排

#### Standard Flow (Single Analysis) / 标准流程（单次分析）

```
Input
  │
  ▼
📥 Intake Agent ──── Parse into structured format
  │
  ▼
🔍 Clarification Agent ──── Flag missing info
  │
  ▼
🪞 Mirror Agent ──── Translate + detect monsters
  │
  ├──▶ 📊 Health Agent ──── Score
  │
  └──▶ 💡 Advisor Agent ──── Generate recommendations
  │
  ▼
Output: Mirror Report
```

#### Deliberation Flow (Multi-Party Conflict) / 审议流程（多方冲突）

Triggered when: ≥ 3 parties involved, or ≥ 2 contradictory positions detected, or user requests "deep arbitration."

触发条件：涉及 ≥ 3 方，或检测到 ≥ 2 个矛盾立场，或用户主动请求「深度仲裁」。

```
Mirror Agent detects conflict
  │
  ▼
Spawn N × Advocate Agents (one per party)
  │
  ▼
┌──────────────── DELIBERATION PROTOCOL ────────────────┐
│                                                        │
│  Round 1: Independent Statements / 各方独立表态          │
│  Each Advocate outputs:                                │
│  - Position (support / oppose / conditional)            │
│  - Core constraints                                    │
│  - Minimum acceptable outcome                          │
│  - Alternative proposal if this path is rejected        │
│                                                        │
│  Round 2: Cross-Examination / 交叉质询                  │
│  Each Advocate responds to others:                     │
│  - Specific contradictions identified                   │
│  - Questions that must be answered                     │
│  - NO vague objections allowed                         │
│                                                        │
│  Round 3: Convergence / 收敛                            │
│  Arbiter Agent synthesizes:                            │
│  - Conflict type classification                        │
│  - Option A / B / C with trade-offs                    │
│  - Who hasn't committed yet                            │
│  - Recommended path + escalation if needed              │
│                                                        │
│  ⚠️ MAX 3 ROUNDS. Exceeding 3 = monster detected.       │
│  ⚠️ 最多 3 轮。超过 3 轮 = 妖怪出没。                     │
└────────────────────────────────────────────────────────┘
```

#### Memory Flow (Cross-Time Analysis) / 记忆流程（跨时间分析）

```
New analysis completed
  │
  ├──▶ 🧠 Memory Agent ──── Store patterns, check against history
  │                          Is this pattern recurring?
  │                          Is this person's 5th phantom support?
  │
  ├──▶ 🔄 Drift Agent ──── Compare current item state vs. original
  │                          Has the goal shifted?
  │                          Has the owner changed quietly?
  │
  └──▶ 🚨 Escalation Agent ──── Check stale thresholds
                                 Generate escalation summary if needed
```

---

<a id="llm-backend"></a>
## LLM Backend / 模型后端

### Multi-Provider Router / 多模型路由

```python
# config.yaml
llm:
  # Primary provider — used by default
  primary:
    provider: "openai"           # openai | qwen | gemini | minimax
    model: "gpt-4o"
    api_key: "${OPENAI_API_KEY}"
    base_url: "https://api.openai.com/v1"    # override for proxies

  # Fallback chain — tried in order if primary fails
  fallback:
    - provider: "qwen"
      model: "qwen-max"
      api_key: "${QWEN_API_KEY}"
      base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
    - provider: "gemini"
      model: "gemini-2.0-flash"
      api_key: "${GEMINI_API_KEY}"
    - provider: "minimax"
      model: "MiniMax-Text-01"
      api_key: "${MINIMAX_API_KEY}"
      group_id: "${MINIMAX_GROUP_ID}"

  # Per-agent model override (optional)
  agent_overrides:
    mirror_agent: "qwen-max"           # Chinese context → Qwen might be better
    arbiter_agent: "gpt-4o"            # Complex reasoning → GPT-4o
    intake_agent: "gemini-2.0-flash"   # Fast parsing → Gemini Flash
```

### Provider Implementation / 接口实现

All providers conform to a unified interface:

所有模型后端遵循统一接口：

```python
class LLMProvider(Protocol):
    async def complete(
        self,
        messages: list[Message],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,  # JSON mode
    ) -> LLMResponse: ...

class LLMRouter:
    """
    Handles provider selection, fallback, and per-agent routing.
    """
    async def complete(
        self,
        messages: list[Message],
        agent_name: Optional[str] = None,  # for agent-specific model override
        **kwargs
    ) -> LLMResponse:
        provider = self._get_provider(agent_name)
        try:
            return await provider.complete(messages, **kwargs)
        except LLMError:
            return await self._fallback(messages, **kwargs)
```

### Supported Providers / 支持的模型

| Provider | Models | Best For | 适合场景 |
|----------|--------|----------|---------|
| OpenAI | GPT-4o, GPT-4o-mini | Complex reasoning, English context | 复杂推理、英文场景 |
| Qwen (通义千问) | Qwen-Max, Qwen-Plus | Chinese context, cost-effective | 中文场景、性价比 |
| Google Gemini | Gemini 2.0 Flash/Pro | Fast processing, multimodal | 快速处理、多模态 |
| MiniMax | MiniMax-Text-01 | Chinese long-context, cost-effective | 中文长上下文、性价比 |

**Adding a new provider**: Implement `LLMProvider` protocol, add to config. That's it.

**添加新模型**：实现 `LLMProvider` 协议，加到配置文件。就这么简单。

---

<a id="bot-integration"></a>
## Bot Integration / Bot 接入

### Feishu Bot / 飞书机器人

Feishu supports custom bots via webhook + event subscription. The bot can:
飞书支持通过 webhook + 事件订阅接入自定义机器人。

```
功能:
- 接收群内 @消息 → 触发分析
- 接收私聊消息 → 匿名分析
- 主动推送 → 周报、事项提醒
- 消息卡片 → 交互式报告（支持/展开/链接）

接入方式:
1. 在飞书开放平台创建应用
2. 启用机器人能力
3. 配置事件订阅（im.message.receive_v1）
4. 部署 webhook 处理服务
```

### WeCom Bot / 企业微信机器人

```
功能:
- 群内 @触发
- Webhook 主动推送
- 消息模板回复

接入方式:
1. 企业微信管理后台 → 应用管理 → 创建应用
2. 启用消息接收
3. 配置回调 URL
```

### Slack Bot

```
Features:
- Slash commands (/mirror, /xray, /report)
- @mention trigger
- Thread-aware analysis
- Scheduled reports via Slack workflows

Setup:
1. Create Slack App
2. Enable Event Subscriptions
3. Add Bot Token Scopes
4. Deploy webhook handler
```

### Bot Interaction Design / Bot 交互设计

```
┌───────────────────────────────────────────────────────────┐
│  群聊场景                                                   │
│                                                            │
│  张三: 那个数据看板需求，我觉得方向上是对的，               │
│       但资源确实紧，我建议下周拉个会对齐...                  │
│                                                            │
│  李四: @照妖镜 帮我们看看这个需求讨论                        │
│                                                            │
│  🪞 照妖镜:                                                 │
│  ┌─────────────────────────────────────────────────┐       │
│  │  📋 事项 X 光片: 数据看板需求                      │       │
│  │                                                   │       │
│  │  ⚠️ 检测到 3 个问题:                               │       │
│  │  • 👻 社交性支持 — 有支持表态但无具体承诺           │       │
│  │  • 🧱 资源黑洞 — 「资源紧」未给出替代方案           │       │
│  │  • 🌀 会议稀释 — 用「拉会对齐」替代直接决策          │       │
│  │                                                   │       │
│  │  💡 建议: 先确认一个 Owner 和具体日期               │       │
│  │     再决定是否需要开会                              │       │
│  │                                                   │       │
│  │  [查看完整报告]  [生成 X 光片]  [发起审议]          │       │
│  └─────────────────────────────────────────────────┘       │
│                                                            │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  私聊场景                                                   │
│                                                            │
│  你: [粘贴一段群聊记录]                                     │
│  你: 帮我看看这段讨论是不是有问题                            │
│                                                            │
│  🪞 照妖镜:                                                 │
│  [匿名化分析结果，角色A/角色B/角色C，仅你可见]               │
│                                                            │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │
│  自扫场景                                                   │
│                                                            │
│  你: @照妖镜 自查                                           │
│                                                            │
│  🪞 照妖镜 (私聊回复):                                      │
│  你在过去一周的群发言中:                                     │
│  • 使用了 3 次 👻社交性支持 表述                              │
│  • 有 2 个承诺尚未跟进                                      │
│  • 建议: 对「API 重构」事项给出具体排期                       │
└───────────────────────────────────────────────────────────┘
```

---

<a id="fool-proof-setup"></a>
## Fool-proof Setup / 傻瓜化配置

### 30 Seconds to Mirror / 30 秒开始照妖

```
┌───────────────────────────────────────────────────────────┐
│                 照妖镜 · 初始配置                            │
│                 ZhaoYaoJing · Setup                         │
│                                                            │
│  Step 1: What kind of org? / 你们是什么组织？                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ 🚀           │ │ 🏢           │ │ 🔬           │          │
│  │ Startup      │ │ Mid/Large   │ │ Research /   │          │
│  │ < 30 people  │ │ Company     │ │ Academic     │          │
│  │ < 30人       │ │ 中大型公司   │ │ 研究院/高校   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                            │
│  Step 2: How do you communicate? / 你们怎么沟通？（多选）    │
│  ☑ WeChat 微信   ☑ Feishu 飞书    ☐ Slack                  │
│  ☐ DingTalk 钉钉  ☑ Email 邮件     ☐ Other 其他             │
│                                                            │
│  Step 3: What hurts most? / 最头疼什么？（选 1-3 个）        │
│  ☐ Requirements never clear / 需求总是扯不清                 │
│  ☐ Things get stuck / 事情总被拖、推不动                     │
│  ☐ Nobody owns anything / 不知道谁在负责                     │
│  ☐ Verbal yes, actual no / 口头答应但不落实                  │
│  ☐ Meetings but no outcomes / 开了无数会没结论               │
│  ☐ Politics but can't name it / 有人搞政治但说不清           │
│                                                            │
│  Step 4: LLM Backend / 选择模型后端                          │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │ 🤖 OpenAI    │ │ 🔮 Qwen     │                           │
│  │ GPT-4o      │ │ 通义千问     │                           │
│  └─────────────┘ └─────────────┘                           │
│  ┌─────────────┐ ┌─────────────┐                           │
│  │ ♊ Gemini    │ │ 🎯 MiniMax  │                           │
│  │ Google      │ │             │                           │
│  └─────────────┘ └─────────────┘                           │
│  API Key: [________________________]                        │
│                                                            │
│  Step 5: Team (optional, add later) / 团队成员（可选）       │
│  [+ Add member: nickname + role/dept]                       │
│  [+ 添加成员: 昵称 + 角色/部门]                               │
│                                                            │
│                   [ 🪞 Start Mirroring / 开始照妖 ]          │
└───────────────────────────────────────────────────────────┘
```

**What the config actually does / 配置做了什么**：
- Org type → adjusts severity thresholds / 组织类型 → 调整严重度阈值
- Communication channels → determines input parser strategy / 沟通方式 → 解析策略
- Pain points → prioritizes relevant pattern scanning / 痛点 → 优先扫描相关 pattern
- LLM backend → routes to selected provider / 模型后端 → 路由到选择的模型
- Team members → identifies role relationships / 团队成员 → 识别角色关系

### Privacy Modes / 隐私模式

```
☑ Anonymous Mode / 匿名模式：All names → Role A / Role B / Role C
☑ Local Mode / 本地模式：Data stays on your device (local LLM)
☐ Cloud Mode / 云端模式：Uses online API (better accuracy, data uploaded)
```

---

<a id="identity-and-org-info"></a>
## Identity & Org Info / 身份与组织信息

### Member Profile (Non-Sensitive Only) / 成员画像（仅非敏感信息）

```yaml
member:
  display_name: "Role A"          # Real name or codename / 真名或代号
  role: "Backend Dev"             # Functional role / 职能角色
  department: "Engineering"       # Department / 部门
  authority_level: "IC"           # IC | TL | Manager | Director | VP
  # ALL OPTIONAL — system works with nothing filled
  # 全部可选——什么都不填系统也能工作
```

### Org Profile / 组织画像

```yaml
org:
  name: ""                        # Optional / 可选
  size: "10-30"                   # For threshold tuning / 用于调整阈值
  type: "startup"                 # startup | corp | research | nonprofit
  departments:
    - name: "Engineering"
      headcount: 8
    - name: "Product"
      headcount: 3
  communication_channels:
    - type: "wechat_group"
      name: "Tech Discussion"
    - type: "feishu"
      name: "All Hands"
```

**Principles / 原则**：
1. **Minimum info**: Mirror doesn't need to know WHO you are, only role relationships
   **最小信息原则**：照妖镜不需要知道你是谁，只需要角色关系
2. **Progressive enrichment**: Start with nothing, add as you go
   **渐进式补充**：一开始啥都不填，用着用着再补
3. **No sensitive data**: Never stores real names, contacts, salary, etc.
   **敏感信息隔离**：不存储真实姓名、联系方式、薪资等隐私数据

---

<a id="input-output-schema"></a>
## Input/Output Schema / 输入输出 Schema

### Input / 输入

```typescript
interface MirrorInput {
  content: string;                        // Raw text / 原始文本
  content_type:
    | "chat_log"                          // Chat records / 聊天记录
    | "meeting_notes"                     // Meeting minutes / 会议纪要
    | "email_thread"                      // Email chain / 邮件链
    | "requirement_doc"                   // Requirement doc / 需求文档
    | "self_check"                        // Self-mirror / 自扫
    | "free_text";                        // Free text / 自由文本
  language: "zh" | "en" | "auto";
  trigger_mode: "manual" | "bot_mention" | "self_mirror"
    | "event_trigger" | "always_on";
  org_config?: OrgConfig;
  members?: Member[];
  related_items?: string[];               // Related item IDs / 关联事项ID
  analysis_focus?: AnalysisFocus[];       // Focus areas / 重点关注
}

type AnalysisFocus =
  | "communication"                       // 沟通层
  | "behavior"                            // 行为层
  | "structural";                         // 系统层
```

### Output / 输出

```typescript
interface MirrorReport {
  // Mirror Translation / 照妖翻译
  translations: {
    original: string;                     // Original text / 原文
    mirror: string;                       // Mirror translation / 照妖翻译
    monster_type?: string;                // Related monster / 关联妖怪
    confidence: number;                   // 0-1
  }[];

  // Monster Detection / 妖怪检测
  monsters_detected: {
    monster_id: string;
    monster_name_zh: string;
    monster_name_en: string;
    severity: 1 | 2 | 3 | 4;
    evidence: string[];                   // Evidence excerpts / 证据原文
    explanation_zh: string;
    explanation_en: string;
  }[];

  // X-Ray (if input is a requirement/item) / X光片
  xray?: {
    objective: string | "unclear";
    deadline: string | "unspecified";
    owner: string | "unassigned";
    dependencies: Dependency[];
    success_criteria: string | "undefined";
    missing_info: string[];
    blockers: Blocker[];
  };

  // Health Score / 健康分数
  health_score: {
    overall: number;                      // 0-100
    dimensions: {
      clarity: number;                    // 信息清晰度
      accountability: number;             // 责任明确度
      momentum: number;                   // 推进力
      trust: number;                      // 信任度
    };
  };

  // Recommendations (serious, not sarcastic) / 建议（认真的）
  recommendations: {
    priority: "high" | "medium" | "low";
    action_zh: string;
    action_en: string;
    rationale_zh: string;
    rationale_en: string;
    addressed_monsters: string[];
  }[];

  // Deliberation result (if agent deliberation was triggered)
  deliberation?: {
    parties: { role: string; position: string; constraints: string[] }[];
    conflict_type: string;
    options: { label: string; description: string; trade_offs: string[] }[];
    unresolved: string[];
    escalation_recommendation?: string;
  };
}
```

---

<a id="tech-stack-and-project-structure"></a>
## Tech Stack & Project Structure / 技术栈与项目结构

### Tech Stack / 技术栈

```
Backend:   Python 3.11+ / FastAPI
Frontend:  React + TypeScript (or plain HTML for ultra-light MVP)
Database:  SQLite (dev) / PostgreSQL (prod)
LLM:       OpenAI / Qwen / Gemini / MiniMax via unified router
Bot SDKs:  feishu-python-sdk / wechatpy / slack-bolt
Deploy:    Docker / Docker Compose
```

### Project Structure / 项目结构

```
zhaoyaojing/
├── README.md                           # This document (bilingual)
├── README_ZH.md                        # Chinese README
├── LICENSE                             # MIT or Apache 2.0
├── docker-compose.yml
├── .env.example
│
├── docs/
│   ├── DESIGN.md                       # Architecture deep-dive
│   ├── MONSTER_CODEX.md                # Full monster codex
│   ├── TRIGGER_GUIDE.md                # Trigger mechanism guide
│   └── CONTRIBUTING.md                 # Contribution guide
│
├── web/                                # Frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── MirrorInput.tsx         # Input panel
│   │   │   ├── MirrorReport.tsx        # Report display
│   │   │   ├── MonsterCard.tsx         # Monster card
│   │   │   ├── XRayPanel.tsx           # X-ray display
│   │   │   ├── HealthScore.tsx         # Health score gauge
│   │   │   ├── SelfMirror.tsx          # Self-mirror mode
│   │   │   └── SetupWizard.tsx         # Fool-proof setup
│   │   └── i18n/                       # Bilingual strings
│   │       ├── zh.json
│   │       └── en.json
│   └── package.json
│
├── server/                             # Backend
│   ├── main.py                         # FastAPI entry
│   ├── config.py                       # Config loader
│   ├── api/
│   │   ├── mirror.py                   # /api/mirror endpoint
│   │   ├── xray.py                     # /api/xray endpoint
│   │   ├── deliberate.py              # /api/deliberate endpoint
│   │   └── report.py                  # /api/report endpoint
│   │
│   ├── agents/
│   │   ├── base.py                     # Base agent class
│   │   ├── intake.py                   # 📥 Intake Agent
│   │   ├── clarification.py           # 🔍 Clarification Agent
│   │   ├── mirror.py                   # 🪞 Mirror Agent
│   │   ├── health.py                   # 📊 Health Agent
│   │   ├── advisor.py                  # 💡 Advisor Agent
│   │   ├── advocate.py                 # 🎭 Advocate Agent
│   │   ├── arbiter.py                  # ⚖️ Arbiter Agent
│   │   ├── memory.py                   # 🧠 Memory Agent
│   │   ├── drift.py                    # 🔄 Drift Agent
│   │   └── escalation.py              # 🚨 Escalation Agent
│   │
│   ├── llm/
│   │   ├── router.py                   # LLM Router
│   │   ├── base.py                     # Provider protocol
│   │   ├── openai_provider.py
│   │   ├── qwen_provider.py
│   │   ├── gemini_provider.py
│   │   └── minimax_provider.py
│   │
│   ├── monsters/
│   │   ├── codex.py                    # Monster codex loader
│   │   └── detector.py                 # Pattern matching logic
│   │
│   ├── prompts/
│   │   ├── translate_zh.md             # Mirror translation prompt (CN)
│   │   ├── translate_en.md             # Mirror translation prompt (EN)
│   │   ├── detect.md                   # Monster detection prompt
│   │   ├── xray.md                     # X-ray generation prompt
│   │   ├── advocate.md                 # Advocate agent prompt
│   │   ├── arbiter.md                  # Arbiter agent prompt
│   │   └── self_mirror.md              # Self-mirror prompt
│   │
│   └── triggers/
│       ├── event_engine.py             # Event trigger engine
│       └── rules.yaml                  # Default trigger rules
│
├── bots/                               # Bot integrations
│   ├── feishu/
│   │   ├── bot.py                      # Feishu bot handler
│   │   └── cards.py                    # Message card templates
│   ├── wecom/
│   │   └── bot.py                      # WeCom bot handler
│   └── slack/
│       └── bot.py                      # Slack bot handler
│
├── config/
│   ├── monsters/
│   │   ├── builtin/                    # Built-in monsters
│   │   │   ├── communication.yaml
│   │   │   ├── behavior.yaml
│   │   │   └── structural.yaml
│   │   └── community/                  # Community-contributed monsters
│   │       └── .gitkeep
│   └── default_config.yaml             # Default org config
│
└── tests/
    ├── test_mirror.py
    ├── test_monsters.py
    ├── test_agents.py
    └── fixtures/                       # Test cases
        ├── chat_log_01.txt
        ├── meeting_notes_01.txt
        └── expected_reports/
```

---

<a id="demo-case"></a>
## Demo Case / 示例

### Input / 输入

```
张三在群里说：
"那个数据看板的需求，老李之前提过，我觉得方向上是对的。
但现在咱们人手确实紧，小王那边还有两个紧急的要先处理。
我建议我们下周拉个会，把产品、前端、数据的人都叫上，
先对齐一下具体怎么做，然后再排期。"
```

### Output / 输出

```
┌──────────────────────────────────────────────────────────┐
│  🪞 照妖翻译 / Mirror Translation                         │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  「那个数据看板的需求，老李之前提过」                         │
│  → 🫥 I'm not the one who proposed this — Li did.         │
│       Pre-emptive liability transfer.                      │
│    → 🫥 不是我提的，是老李提的。提前免责。                    │
│                                                           │
│  「我觉得方向上是对的」                                     │
│  → 👻 Verbal support. No commitment to any actual action.  │
│    → 👻 口头支持，不代表我会做任何事。                        │
│                                                           │
│  「但现在咱们人手确实紧」                                   │
│  → 🧱 Resource veto activated.                             │
│    → 🧱 资源否决权已激活。                                   │
│                                                           │
│  「小王那边还有两个紧急的要先处理」                           │
│  → 📈 Prerequisites starting to inflate.                    │
│    → 📈 前置条件开始膨胀。                                   │
│                                                           │
│  「我建议我们下周拉个会」                                   │
│  → 🌀 Meeting vortex initiated.                            │
│    → 🌀 会议稀释启动。                                      │
│                                                           │
│  「把产品、前端、数据的人都叫上」                             │
│  → 💨 Diffusion in progress. More people = less ownership.  │
│    → 💨 责任扩散中。拉更多人 = 更没人负责。                   │
│                                                           │
│  「先对齐一下具体怎么做，然后再排期」                         │
│  → 🦊 Classic two-stage delay: align → schedule → re-eval  │
│       → forget.                                            │
│    → 🦊 经典拖延链：对齐→排期→再评估→忘了。                  │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  🔍 Monsters Detected / 检测到的妖怪                       │
│                                                           │
│  🟡 Lv.2  👻 Phantom Ally / 社交性支持妖                    │
│  🟡 Lv.2  🧱 Resource Void / 资源黑洞妖                    │
│  🟢 Lv.1  🌀 Meeting Vortex / 会议稀释妖                   │
│  🟢 Lv.1  💨 Diffusion Ghost / 责任扩散妖                   │
│  🟢 Lv.1  🦊 Eternal Evaluator / 评估拖延妖                │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  💡 Recommendations (serious) / 建议（认真的）              │
│                                                           │
│  1. [HIGH] Ask directly: "Are you willing to own this?"    │
│     直接问张三：「你愿意做 owner 吗？」                       │
│     If no, ask who will. If nobody → formally shelve.       │
│     不愿意就问谁来。没人来就正式搁置，别拖着。                │
│                                                           │
│  2. [HIGH] No meeting needed. Ask 3 questions in chat:     │
│     不需要开会。在群里直接问：                                │
│     - What's the MVP?   MVP 是什么？                        │
│     - Who owns it?      谁来做？（一个名字）                  │
│     - When's v1?        什么时候出第一版？（一个日期）         │
│     Can't answer = not ready to do.                         │
│     答不出来 = 还没到做的时候。                               │
│                                                           │
│  3. [MED] If "tight resources" is real, demand specifics.  │
│     「人手紧」如果是真的，要求给出小王的排期表，               │
│     以及最早可开始的时间。不给时间 = 隐性拒绝。               │
│                                                           │
├──────────────────────────────────────────────────────────┤
│  📊 Health Score / 组织健康分: 62/100                       │
│  Clarity 清晰度: 45 | Accountability 责任度: 35            │
│  Momentum 推进力: 50 | Trust 信任度: 78                     │
└──────────────────────────────────────────────────────────┘
```

---

<a id="community"></a>
## Community / 开源社区

### Monster Codex is the Core Contribution Entry / 妖怪图鉴是社区贡献的核心入口

Anyone can PR a new monster:

```yaml
# File: config/monsters/community/passive_aggressive_approver.yaml

id: passive_aggressive_approver
name_zh: "阴阳怪气审批妖"
name_en: "The Passive-Aggressive Approver"
category: communication
description_zh: "审批通过但措辞暗含不满，让被审批者赢了但不敢开心"
description_en: "Approves but with undertones of displeasure"
detection_signals:
  - pattern_zh: "可以做，你们自己定吧"
    pattern_en: "Fine, you guys decide"
  - pattern_zh: "行吧，就这样吧"
    pattern_en: "Sure, whatever"
  - pattern_zh: "审批通过但不给任何正面回应"
    pattern_en: "Approved with zero positive acknowledgment"
classic_lines_zh:
  - "可以，你们自己把握吧"
  - "行，我没意见，你们推进就好"
classic_lines_en:
  - "Fine, just handle it yourselves"
  - "Sure, I have no opinion, go ahead"
severity_range: [1, 2]
contributed_by: "github_username"
```

### Contribution Paths / 贡献路径

| Type | Difficulty | Entry Point |
|------|-----------|-------------|
| Submit new monster / 提交新妖怪 | ⭐ | YAML + PR |
| Submit translation samples / 提交照妖翻译语料 | ⭐ | Issue or form |
| Improve detection prompts / 改进检测 Prompt | ⭐⭐ | PR to prompts/ |
| Add bot adapter / 新增 Bot 适配 | ⭐⭐⭐ | PR to bots/ |
| Improve agent protocols / 改进 Agent 协议 | ⭐⭐⭐⭐ | PR to agents/ |
| Add LLM provider / 新增模型后端 | ⭐⭐ | PR to llm/ |

---

<a id="faq"></a>
## FAQ

**Q: Isn't this just AI-powered office gossip?**
**Q: 这不就是让 AI 搞办公室八卦吗？**

A: Gossip is anonymous, one-sided, and emotional. ZhaoYaoJing is structured, traceable, and comes with constructive recommendations. The difference is whether the output can be discussed openly.
A: 八卦是匿名的、片面的、情绪化的。照妖镜是结构化的、可追溯的、有建设性建议的。区别在于输出物能不能被拿到台面上讨论。

**Q: Won't this make team relationships more tense?**
**Q: 这会不会让组织关系更紧张？**

A: What actually creates tension is ambiguity and suspicion. Putting problems on the table may be uncomfortable short-term, but builds real trust long-term.
A: 真正让关系紧张的是模糊和猜疑。把问题摆到明面上，短期可能不舒服，长期会建立真正的信任。

**Q: What if management doesn't want to use it?**
**Q: 如果管理层不想用怎么办？**

A: ZhaoYaoJing's first user doesn't need to be management. Any IC suffering from internal friction can use it personally first, then bring the report to their lead. Bottom-up adoption beats top-down deployment.
A: 照妖镜的第一使用者不需要是管理层。任何被内耗折磨的 IC 都可以先自己用，拿着报告去找 leader 谈。自下而上比自上而下更有效。

**Q: Is the AI accurate?**
**Q: AI 的判断准吗？**

A: ZhaoYaoJing doesn't make verdicts — it makes the invisible visible. Like an X-ray doesn't diagnose, but without it the doctor can't see the fracture.
A: 照妖镜不做「判决」，只做「显影」。就像 X 光片不替医生做诊断，但没有 X 光片医生也看不见骨折。

**Q: What about privacy?**
**Q: 隐私怎么办？**

A: Supports fully local operation (local LLM), anonymous mode (auto-replace names), no mandatory internet. Your org's dirty laundry doesn't need to be shown to anyone.
A: 支持完全本地运行、匿名模式、不强制联网。你的组织脏衣服不需要晒给任何人看。

**Q: Why the name "ZhaoYaoJing"?**
**Q: 为什么叫照妖镜？**

A: 照妖镜 is a mythical Chinese mirror that reveals monsters disguised as humans. In Chinese culture, it's one of the most instantly recognizable metaphors for "seeing through bullshit." The name works because it's playful (people try it for fun), cultural (deeply resonant for Chinese-speaking teams), and accurate (it literally describes what the tool does).

---

## Project Identity / 项目品牌

| Element | Content |
|---------|---------|
| Chinese Name / 中文名 | 照妖镜 |
| English Name / 英文名 | ZhaoYaoJing — OrgMirror |
| Tagline CN | 把办公室里的妖魔鬼怪照出原形 |
| Tagline EN | Strip the bullshit. See the real org. |
| GitHub Repo | `zhaoyaojing` |
| Logo Concept | Ancient bronze mirror reflecting monster emojis / 古铜镜映射妖怪 emoji |

---

## Quick Start / 快速开始

```bash
# Clone
git clone https://github.com/YOUR_ORG/zhaoyaojing.git
cd zhaoyaojing

# Configure
cp .env.example .env
# Edit .env with your LLM API key

# Run
docker-compose up

# Open http://localhost:3000
# Start mirroring. 开始照妖。
```

---

*ZhaoYaoJing is open source under [MIT/Apache 2.0]. Contributions welcome.*

*照妖镜是开源项目。欢迎贡献新妖怪。*
