import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    group_id: int
    webhook_url: str
    port: int


def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    group_id_raw = os.getenv("GROUP_ID", "").strip()
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    port_raw = os.getenv("PORT", "8443").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN is required")

    if not group_id_raw:
        raise ValueError("GROUP_ID is required")

    try:
        group_id = int(group_id_raw)
    except ValueError as exc:
        raise ValueError("GROUP_ID must be an integer Telegram chat ID") from exc

    if not webhook_url:
        raise ValueError("WEBHOOK_URL is required")

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("PORT must be an integer") from exc

    return Settings(
        bot_token=bot_token,
        group_id=group_id,
        webhook_url=webhook_url.rstrip("/"),
        port=port,
    )
