import logging
import requests
from config import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)
API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(chat_id: int, text: str) -> None:
    try:
        requests.post(
            f"{API}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=30,
        )
    except Exception as e:
        logger.error("send_message failed chat_id=%s: %s", chat_id, e)


def set_webhook(url: str, secret: str = "") -> None:
    params = {"url": url}
    if secret:
        params["secret_token"] = secret
    r = requests.get(f"{API}/setWebhook", params=params, timeout=30)
    logger.info("setWebhook: %s", r.text)
