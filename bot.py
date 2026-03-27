import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import get_settings
from database import init_db
from handlers import error_handler, handle_group_reply, handle_private_message, start_command


logging.basicConfig(
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_private_handler(settings):
    async def _handler(update, context):
        await handle_private_message(update, context, settings)

    return _handler


def build_group_reply_handler(settings):
    async def _handler(update, context):
        await handle_group_reply(update, context, settings)

    return _handler


def main() -> None:
    settings = get_settings()
    init_db()

    app = Application.builder().token(settings.bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            build_private_handler(settings),
        )
    )
    app.add_handler(
        MessageHandler(
            filters.Chat(settings.group_id) & filters.REPLY,
            build_group_reply_handler(settings),
        )
    )

    app.add_error_handler(error_handler)

    webhook_path = f"webhook/{settings.bot_token}"
    webhook_url = f"{settings.webhook_url}/{webhook_path}"

    logger.info("Starting bot in webhook mode on port %s", settings.port)
    app.run_webhook(
        listen="0.0.0.0",
        port=settings.port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
