# Bot Setup Guide / Bot 接入指南

照妖镜支持三个聊天平台。每个平台的接入流程大约 15 分钟。

---

## Feishu / 飞书

### Step 1: Create App / 创建应用

1. 打开 [飞书开放平台](https://open.feishu.cn/app)
2. 点击「创建企业自建应用」
3. 填写应用名称：**照妖镜** (或你喜欢的名字)
4. 记录 `App ID` 和 `App Secret`

### Step 2: Enable Bot / 启用机器人

1. 在应用详情页，左侧菜单点击「添加应用能力」→「机器人」
2. 启用机器人能力

### Step 3: Configure Permissions / 配置权限

在「权限管理」中申请以下权限：

| 权限 | 说明 |
|------|------|
| `im:message:send_as_bot` | 以机器人身份发送消息 |
| `im:message` | 获取与发送单聊、群聊消息 |
| `im:chat` | 获取群信息 |

### Step 4: Event Subscription / 事件订阅

1. 左侧菜单 →「事件订阅」
2. 请求地址填写：`https://your-domain.com/api/bot/feishu/webhook`
3. 添加事件：
   - `im.message.receive_v1` — 接收消息
4. 记录页面上的 `Verification Token` 和 `Encrypt Key`

### Step 5: Configure .env / 配置环境变量

```bash
FEISHU_APP_ID=cli_a5xxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxx  # 可选
```

### Step 6: Publish App / 发布应用

1. 在应用详情页点击「版本管理与发布」
2. 创建版本 → 提交审核
3. 管理员审批通过后，机器人即可在群中使用

### Step 7: Test / 测试

1. 在飞书群中添加机器人「照妖镜」
2. 发送：`@照妖镜 扫描`
3. 或引用一段讨论后 `@照妖镜`

### 可用命令

```
@照妖镜 扫描            → 扫描最近群消息
@照妖镜 事项 [描述]      → 生成 X 光片
@照妖镜 自查            → 私聊返回你最近发言的分析
@照妖镜 周报            → 本周妖气报告
@照妖镜 复盘 [事项]      → 事项复盘
```

---

## WeCom / 企业微信

### Step 1: Create App / 创建应用

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 应用管理 → 自建 → 创建应用
3. 填写应用名称：**照妖镜**
4. 记录 `CorpID`（在「我的企业」页面顶部）
5. 记录应用的 `AgentId` 和 `Secret`

### Step 2: Configure Callback / 配置回调

1. 在应用详情页 → 「接收消息」→ 设置 API 接收
2. URL: `https://your-domain.com/api/bot/wecom/webhook`
3. Token: 自己填一个（记下来）
4. EncodingAESKey: 点击「随机获取」（记下来）
5. 点击保存 — 企业微信会向你的 URL 发送验证请求

### Step 3: Configure .env / 配置环境变量

```bash
WECOM_CORP_ID=ww1234567890
WECOM_AGENT_ID=1000001
WECOM_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
WECOM_TOKEN=your_token
WECOM_ENCODING_AES_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 4: Test / 测试

1. 在企业微信中找到「照妖镜」应用
2. 发送消息或在群中 @照妖镜

---

## Slack

### Step 1: Create App / 创建应用

1. 打开 [Slack API](https://api.slack.com/apps) → Create New App
2. 选择 "From scratch"
3. App Name: **ZhaoYaoJing**
4. 选择你的 Workspace

### Step 2: Bot Token Scopes / 权限配置

在 OAuth & Permissions 页面，添加以下 Bot Token Scopes：

| Scope | 说明 |
|-------|------|
| `app_mentions:read` | 读取 @mention |
| `chat:write` | 发送消息 |
| `channels:history` | 读取频道历史 |
| `groups:history` | 读取私有频道历史 |
| `im:history` | 读取私聊历史 |
| `im:write` | 发送私聊 |
| `commands` | 注册 slash commands |

### Step 3: Event Subscriptions / 事件订阅

1. 左侧菜单 → Event Subscriptions → Enable Events
2. Request URL: `https://your-domain.com/api/bot/slack/events`
3. Subscribe to bot events:
   - `app_mention` — @mention
   - `message.im` — 私聊消息

### Step 4: Slash Commands / 注册命令

1. 左侧菜单 → Slash Commands → Create New Command
2. 创建以下命令：

| Command | Request URL | Description |
|---------|------------|-------------|
| `/mirror` | `https://your-domain.com/api/bot/slack/commands` | Analyze text with ZhaoYaoJing |
| `/xray` | `https://your-domain.com/api/bot/slack/commands` | Generate X-ray for an item |
| `/report` | `https://your-domain.com/api/bot/slack/commands` | Generate weekly report |

### Step 5: Install App / 安装应用

1. 左侧菜单 → Install App → Install to Workspace
2. 授权后获取 `Bot User OAuth Token` (xoxb-...)
3. 在 Basic Information 页面获取 `Signing Secret`

### Step 6: Configure .env / 配置环境变量

```bash
SLACK_BOT_TOKEN=xoxb-1234567890-1234567890123-xxxxxxxxxxxxxxxxxxxx
SLACK_SIGNING_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SLACK_APP_TOKEN=xapp-1-xxxxxxxxxxxx-xxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Step 7: Test / 测试

1. 在 Slack 频道中 `@ZhaoYaoJing` + 一段讨论
2. 或使用 `/mirror 粘贴一段文本`

---

## Troubleshooting / 常见问题

### "Webhook verification failed" / 验证失败

确保：
1. URL 是 HTTPS 且可公网访问
2. 服务器正在运行 (`curl https://your-domain.com/api/health`)
3. `.env` 中的 Token/Secret 与平台配置一致

### "Bot doesn't respond" / 机器人没反应

1. 检查服务器日志：`docker-compose logs -f server`
2. 确认 LLM API key 有效：调用 `/api/mirror` 测试
3. 确认机器人已被添加到群/频道

### "Response too slow" / 回复太慢

MiniMax M2.7 是 thinking model，首次响应需要 15-30 秒。这是正常的。
如果需要更快响应，考虑：
1. 使用更快的模型（如 Qwen-Plus、GPT-4o-mini）
2. 在 bot handler 中先回复"分析中..."，然后异步发送结果

### "Chinese characters garbled" / 中文乱码

确保：
1. 数据库使用 UTF-8 编码
2. Docker container locale 设置正确
3. nginx 配置中添加 `charset utf-8;`
