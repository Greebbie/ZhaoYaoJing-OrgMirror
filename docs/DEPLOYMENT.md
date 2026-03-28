# Deployment Guide / 部署指南

## Quick Overview / 快速概览

```
你的选择:
┌─────────────────────────────────────────────────────┐
│  A. VPS + Docker     → 适合正式使用，接入飞书/企微     │
│  B. Railway/Render   → 一键部署，适合 Demo            │
│  C. 本地 + ngrok     → 开发测试 Bot webhook           │
└─────────────────────────────────────────────────────┘
```

---

## Option A: VPS + Docker Compose (Recommended for Production)

### Prerequisites / 前置条件

- A VPS (2 vCPU, 4GB RAM minimum) — Alibaba Cloud, Tencent Cloud, AWS, etc.
- A domain name pointed to your VPS IP
- Docker & Docker Compose installed

### Step 1: Clone & Configure / 克隆配置

```bash
# On your server
git clone https://github.com/your-org/zhaoyaojing.git
cd zhaoyaojing

# Copy and edit environment variables
cp .env.example .env
nano .env  # Fill in your LLM API key + bot credentials
```

**Minimum `.env` for just Web UI (no bots):**
```bash
MINIMAX_API_KEY=sk-your-key
MINIMAX_MODEL=minimax-m2.7
```

**Full `.env` with Feishu bot:**
```bash
MINIMAX_API_KEY=sk-your-key
MINIMAX_MODEL=minimax-m2.7
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_VERIFICATION_TOKEN=xxx
POSTGRES_PASSWORD=your-secure-password
```

### Step 2: SSL Certificate / 证书配置

```bash
# Install certbot
apt install certbot

# Get certificate (replace with your domain)
certbot certonly --standalone -d your-domain.com

# Update nginx/nginx.conf — replace "your-domain.com" with your actual domain
sed -i 's/your-domain.com/your-actual-domain.com/g' nginx/nginx.conf
```

### Step 3: Deploy / 部署

```bash
# Production deploy
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# Check logs
docker-compose -f docker-compose.prod.yml logs -f server
```

### Step 4: Verify / 验证

```bash
# Health check
curl https://your-domain.com/api/health
# Expected: {"status":"ok","service":"zhaoyaojing","version":"0.1.0"}

# API docs
open https://your-domain.com/docs

# Frontend
open https://your-domain.com
```

### Step 5: Configure Bot Webhooks / 配置 Bot

See [BOT_SETUP_GUIDE.md](BOT_SETUP_GUIDE.md) for platform-specific setup.

Your webhook URLs will be:
```
Feishu:  https://your-domain.com/api/bot/feishu/webhook
WeCom:   https://your-domain.com/api/bot/wecom/webhook
Slack:   https://your-domain.com/api/bot/slack/events
         https://your-domain.com/api/bot/slack/commands
```

---

## Option B: Railway / Render (One-Click Deploy)

For demo or small teams that don't want to manage a server.

### Railway

1. Fork the repo to your GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables in Railway dashboard
4. Railway auto-detects the Dockerfile and deploys
5. Get your public URL: `https://your-app.up.railway.app`
6. Use that URL for bot webhook configuration

### Render

1. Fork the repo
2. Go to [render.com](https://render.com) → New Web Service → Connect repo
3. Settings:
   - Build Command: `pip install -e .`
   - Start Command: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard
5. Deploy

**Note:** Railway/Render free tiers may have cold start delays. Use paid tier for production bots (webhook timeouts are typically 3-5 seconds).

---

## Option C: Local + ngrok (Development / Testing)

For testing bot webhooks without deploying to a server.

### Step 1: Start the Server Locally

```bash
cd zhaoyaojing
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -e ".[dev]"
cd web && npm install && cd ..

# Start backend
uvicorn server.main:app --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd web && npm run dev
```

### Step 2: Expose with ngrok

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
```

ngrok gives you a public URL like `https://abc123.ngrok-free.app`

### Step 3: Configure Bot Webhook

Use the ngrok URL as your webhook base:
```
Feishu:  https://abc123.ngrok-free.app/api/bot/feishu/webhook
WeCom:   https://abc123.ngrok-free.app/api/bot/wecom/webhook
Slack:   https://abc123.ngrok-free.app/api/bot/slack/events
```

**Note:** ngrok URLs change every restart (unless on paid plan). Update webhook URLs each time.

---

## Database / 数据库

### Development (Default)
SQLite — no configuration needed. A file `zhaoyaojing.db` is created automatically.

### Production
Switch to PostgreSQL by setting `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/zhaoyaojing
```

The `docker-compose.prod.yml` already includes a PostgreSQL service and wires it up automatically.

---

## Troubleshooting / 常见问题

### Server won't start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs server

# Common fixes:
# 1. Missing API key → Add at least one LLM key to .env
# 2. Database connection failed → Check PostgreSQL is running
# 3. Port conflict → Change SERVER_PORT in .env
```

### Bot webhook not responding
```bash
# 1. Check webhook URL is correct and HTTPS
curl -X POST https://your-domain.com/api/bot/feishu/webhook \
  -H "Content-Type: application/json" \
  -d '{"challenge":"test"}'

# 2. Check bot env vars are set
docker-compose -f docker-compose.prod.yml exec server env | grep FEISHU

# 3. Check server logs for webhook events
docker-compose -f docker-compose.prod.yml logs -f server | grep "bot"
```

### LLM calls timing out
- MiniMax M2.7 thinking models can take 30-60 seconds
- Ensure `proxy_read_timeout` in nginx is set to 120s
- Check your API key balance/quota on the provider dashboard
