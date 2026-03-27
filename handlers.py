import html
import logging

from telegram import Update
from telegram.constants import ChatType
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import ContextTypes

from config import Settings
from database import get_user_id, save_mapping

logger = logging.getLogger(__name__)


def _format_sender(user) -> str:
    full_name = html.escape(user.full_name)
    username = f"@{html.escape(user.username)}" if user.username else "(no username)"
    user_id = user.id
    return (
        "New inbox message\n"
        f"Name: {full_name}\n"
        f"Username: {username}\n"
        f"User ID: <code>{user_id}</code>"
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_chat.type == ChatType.PRIVATE:
        await update.message.reply_text(
            "Welcome! Send me any message and I will forward it to the team."
        )


async def handle_private_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    settings: Settings,
) -> None:
    if not update.effective_message or not update.effective_user or not update.effective_chat:
        return

    if update.effective_chat.type != ChatType.PRIVATE:
        return

    source_message = update.effective_message
    sender = update.effective_user

    try:
        copied = await context.bot.copy_message(
            chat_id=settings.group_id,
            from_chat_id=source_message.chat_id,
            message_id=source_message.message_id,
        )

        sender_info = await context.bot.send_message(
            chat_id=settings.group_id,
            text=_format_sender(sender),
            reply_to_message_id=copied.message_id,
            parse_mode="HTML",
        )

        save_mapping(copied.message_id, sender.id)
        save_mapping(sender_info.message_id, sender.id)
    except TelegramError:
        logger.exception("Failed to forward private message to group")


async def handle_group_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    settings: Settings,
) -> None:
    if not update.effective_message or not update.effective_chat:
        return

    message = update.effective_message
    chat = update.effective_chat

    if chat.id != settings.group_id:
        return

    if not message.reply_to_message:
        return

    target_user_id = get_user_id(message.reply_to_message.message_id)
    if not target_user_id:
        return

    try:
        await context.bot.copy_message(
            chat_id=target_user_id,
            from_chat_id=chat.id,
            message_id=message.message_id,
        )
    except Forbidden:
        logger.warning("Cannot deliver reply to user %s (bot blocked or chat unavailable)", target_user_id)
    except BadRequest as exc:
        logger.warning("Bad request while delivering reply to user %s: %s", target_user_id, exc)
    except TelegramError:
        logger.exception("Unexpected Telegram error while delivering reply to user %s", target_user_id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error

    if isinstance(err, Forbidden):
        logger.warning("Forbidden error: %s", err)
        return

    logger.exception("Unhandled exception while processing update", exc_info=err)
