#!/bin/bash
set -e

echo "================================================"
echo "  ZhaoYaoJing Deploy Script / 照妖镜部署脚本"
echo "================================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found. Install Docker first."
    echo "  https://docs.docker.com/engine/install/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "ERROR: Docker Compose not found."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env

    echo ""
    echo "Please configure your .env file:"
    echo "  1. Add at least one LLM API key"
    echo "  2. Set POSTGRES_PASSWORD for production"
    echo "  3. (Optional) Add bot credentials for Feishu/WeCom/Slack"
    echo ""
    echo "Edit now:"
    echo "  nano .env"
    echo ""
    echo "Then re-run this script."
    exit 0
fi

# Check for LLM key
if ! grep -qE "^(OPENAI_API_KEY|QWEN_API_KEY|GEMINI_API_KEY|MINIMAX_API_KEY)=.+" .env; then
    echo "WARNING: No LLM API key found in .env"
    echo "At least one is required for the mirror to work."
    echo "Edit .env and add your API key."
    exit 1
fi

echo "Configuration found. Starting deployment..."
echo ""

# Choose deployment mode
echo "Select deployment mode:"
echo "  1) Development (SQLite, no SSL)"
echo "  2) Production (PostgreSQL, nginx, SSL)"
read -p "Choice [1/2]: " mode

if [ "$mode" = "2" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
    echo ""
    echo "Production mode selected."
    echo "Make sure you have:"
    echo "  - SSL certificates in /etc/letsencrypt/"
    echo "  - nginx/nginx.conf configured with your domain"
    echo ""
else
    COMPOSE_FILE="docker-compose.yml"
    echo "Development mode selected."
fi

# Deploy
echo ""
echo "Starting services..."
docker compose -f "$COMPOSE_FILE" up -d --build

# Wait for health
echo ""
echo "Waiting for server to start..."
for i in $(seq 1 30); do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "Server is ready!"
        break
    fi
    sleep 2
done

# Verify
echo ""
echo "================================================"
echo "  Deployment Complete!"
echo "================================================"
echo ""
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo ""
echo "Bot Webhook URLs (use your public domain):"
echo "  Feishu:  https://YOUR-DOMAIN/api/bot/feishu/webhook"
echo "  WeCom:   https://YOUR-DOMAIN/api/bot/wecom/webhook"
echo "  Slack:   https://YOUR-DOMAIN/api/bot/slack/events"
echo ""
echo "See docs/BOT_SETUP_GUIDE.md for platform setup."
echo ""

# Health check
curl -s http://localhost:8000/api/health | python3 -m json.tool 2>/dev/null || true
