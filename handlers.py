import logging
from telegram_api import send_message
from deepseek_client import ask, DeepSeekError
from session_store import reset

logger = logging.getLogger(__name__)


def handle_start(chat_id: int, _text: str) -> None:
    send_message(chat_id, "Привет! Напиши вопрос — отвечу через DeepSeek.\n/reset — очистить историю.")


def handle_reset(chat_id: int, _text: str) -> None:
    reset(chat_id)
    send_message(chat_id, "История очищена.")


def handle_text(chat_id: int, text: str) -> None:
    try:
        answer = ask(chat_id, text)
    except DeepSeekError as e:
        logger.warning("deepseek error chat_id=%s: %s", chat_id, e)
        answer = str(e)
    send_message(chat_id, answer)


COMMANDS = {
    "/start": handle_start,
    "/reset": handle_reset,
}


def handle_update(update: dict) -> None:
    msg = update.get("message")
    if not msg:
        return
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    if not text:
        return
    handler = COMMANDS.get(text)
    if handler:
        handler(chat_id, text)
    else:
        handle_text(chat_id, text)
