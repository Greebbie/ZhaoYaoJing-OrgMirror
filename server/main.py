import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.admin import router as admin_router
from server.api.dashboard import router as dashboard_router
from server.api.deliberate import router as deliberate_router
from server.api.items import router as items_router
from server.api.members import router as members_router
from server.api.mirror import router as mirror_router
from server.api.mirror_stream import router as mirror_stream_router
from server.api.reports import router as reports_router
from server.api.self_mirror import router as self_mirror_router
from server.api.triggers import router as triggers_router
from server.api.xray import router as xray_router
from server.config import settings
from server.db.database import init_db

logger = logging.getLogger(__name__)

# Bot routers — optional, log if unavailable
feishu_router = None
wecom_router = None
slack_router = None

try:
    from bots.feishu.router import router as feishu_router
except ImportError as e:
    logger.info("Feishu bot not loaded: %s", e)
try:
    from bots.wecom.router import router as wecom_router
except ImportError as e:
    logger.info("WeCom bot not loaded: %s", e)
try:
    from bots.slack.router import router as slack_router
except ImportError as e:
    logger.info("Slack bot not loaded: %s", e)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("ZhaoYaoJing started — CORS origins: %s", settings.cors_origins)
    yield


app = FastAPI(
    title="ZhaoYaoJing",
    description="AI framework for detecting organizational dysfunction patterns",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mirror_router)
app.include_router(mirror_stream_router)
app.include_router(self_mirror_router)
app.include_router(xray_router)
app.include_router(reports_router)
app.include_router(deliberate_router)
app.include_router(items_router)
app.include_router(triggers_router)
app.include_router(dashboard_router)
app.include_router(admin_router)
app.include_router(members_router)

if feishu_router:
    app.include_router(feishu_router)
if wecom_router:
    app.include_router(wecom_router)
if slack_router:
    app.include_router(slack_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "zhaoyaojing", "version": "0.1.0"}
