"""Slack application configuration.

All sensitive values are read from environment variables.
"""

from pydantic_settings import BaseSettings


class SlackConfig(BaseSettings):
    """Configuration for the Slack bot integration.

    Environment variables:
        SLACK_BOT_TOKEN: Slack bot OAuth token (xoxb-...).
        SLACK_SIGNING_SECRET: Slack signing secret for request verification.
        SLACK_APP_TOKEN: Slack app-level token for Socket Mode (xapp-...).
        SLACK_BOT_NAME: Display name used for mention detection.
        SLACK_API_BASE_URL: Base URL for Slack Web API.
        MIRROR_API_BASE_URL: Base URL for the internal ZhaoYaoJing API.
    """

    bot_token: str = ""
    signing_secret: str = ""
    app_token: str = ""
    bot_name: str = "ZhaoYaoJing"
    api_base_url: str = "https://slack.com/api"
    mirror_api_base_url: str = "http://localhost:8000"

    model_config = {
        "env_prefix": "SLACK_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_slack_config() -> SlackConfig:
    """Create a SlackConfig instance from environment."""
    return SlackConfig()


slack_config = get_slack_config()
