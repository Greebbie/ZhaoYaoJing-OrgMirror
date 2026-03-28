"""Feishu (Lark) application configuration.

All sensitive values are read from environment variables.
"""

from pydantic_settings import BaseSettings


class FeishuConfig(BaseSettings):
    """Configuration for the Feishu bot integration.

    Environment variables:
        FEISHU_APP_ID: Feishu app ID from the developer console.
        FEISHU_APP_SECRET: Feishu app secret.
        FEISHU_VERIFICATION_TOKEN: Token used to verify webhook authenticity.
        FEISHU_ENCRYPT_KEY: Optional encryption key for event payloads.
        FEISHU_BOT_NAME: Display name used for mention detection.
        FEISHU_API_BASE_URL: Base URL for Feishu Open API.
        MIRROR_API_BASE_URL: Base URL for the internal ZhaoYaoJing API.
    """

    app_id: str = ""
    app_secret: str = ""
    verification_token: str = ""
    encrypt_key: str = ""
    bot_name: str = "\u7167\u5996\u955c"  # default: "照妖镜"
    api_base_url: str = "https://open.feishu.cn/open-apis"
    mirror_api_base_url: str = "http://localhost:8000"

    model_config = {
        "env_prefix": "FEISHU_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_feishu_config() -> FeishuConfig:
    """Create a FeishuConfig instance from environment."""
    return FeishuConfig()


feishu_config = get_feishu_config()
