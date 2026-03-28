"""WeCom (WeChat Work) application configuration.

All sensitive values are read from environment variables.
"""

from pydantic_settings import BaseSettings


class WeComConfig(BaseSettings):
    """Configuration for the WeCom bot integration.

    Environment variables:
        WECOM_CORP_ID: WeCom corporation ID.
        WECOM_AGENT_ID: WeCom agent/application ID.
        WECOM_SECRET: WeCom application secret.
        WECOM_TOKEN: Token used to verify webhook authenticity.
        WECOM_ENCODING_AES_KEY: AES key for encrypting/decrypting messages.
        WECOM_BOT_NAME: Display name used for mention detection.
        WECOM_API_BASE_URL: Base URL for WeCom API.
        MIRROR_API_BASE_URL: Base URL for the internal ZhaoYaoJing API.
    """

    corp_id: str = ""
    agent_id: str = ""
    secret: str = ""
    token: str = ""
    encoding_aes_key: str = ""
    bot_name: str = "\u7167\u5996\u955c"  # default: "照妖镜"
    api_base_url: str = "https://qyapi.weixin.qq.com/cgi-bin"
    mirror_api_base_url: str = "http://localhost:8000"

    model_config = {
        "env_prefix": "WECOM_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_wecom_config() -> WeComConfig:
    """Create a WeComConfig instance from environment."""
    return WeComConfig()


wecom_config = get_wecom_config()
