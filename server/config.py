import logging

from pydantic import field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # LLM - Primary
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # LLM - Qwen (fallback)
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-max"

    # LLM - Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # LLM - MiniMax
    minimax_api_key: str = ""
    minimax_group_id: str = ""
    minimax_model: str = "minimax-m2.7"

    # Database
    database_url: str = "sqlite+aiosqlite:///./zhaoyaojing.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Support comma-separated string from env: CORS_ORIGINS=http://a.com,http://b.com"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()

# Warn if no LLM keys are configured
if not any([
    settings.openai_api_key,
    settings.qwen_api_key,
    settings.gemini_api_key,
    settings.minimax_api_key,
]):
    logger.warning(
        "No LLM API keys configured! Set at least one in .env "
        "(OPENAI_API_KEY, QWEN_API_KEY, GEMINI_API_KEY, or MINIMAX_API_KEY)"
    )
