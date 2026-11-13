import logging
import requests
from config import DEEPSEEK_URL, DEEPSEEK_KEY, DEFAULT_MODEL
from session_store import get_history, append, pop_last

logger = logging.getLogger(__name__)


class DeepSeekError(Exception):
    pass


def ask(chat_id: int, user_text: str) -> str:
    append(chat_id, "user", user_text)
    headers = {"Content-Type": "application/json"}
    if DEEPSEEK_KEY:
        headers["Authorization"] = f"Bearer {DEEPSEEK_KEY}"

    payload = {
        "model": DEFAULT_MODEL,
        "messages": get_history(chat_id),
        "stream": False,
    }

    try:
        r = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=180)
    except requests.Timeout:
        pop_last(chat_id)
        raise DeepSeekError("Превышено время ожидания ответа от модели.")
    except requests.RequestException as e:
        pop_last(chat_id)
        raise DeepSeekError(f"Сетевая ошибка: {e}")

    if r.status_code in (401, 403):
        pop_last(chat_id)
        raise DeepSeekError("Сессия DeepSeek недействительна. Нужно обновить auth-файл.")
    if r.status_code == 429:
        pop_last(chat_id)
        raise DeepSeekError("Лимит запросов. Попробуйте позже.")
    if not r.ok:
        pop_last(chat_id)
        raise DeepSeekError(f"Ошибка прокси: HTTP {r.status_code}")

    try:
        answer = r.json()["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        pop_last(chat_id)
        raise DeepSeekError(f"Некорректный ответ прокси: {e}")

    append(chat_id, "assistant", answer)
    return answer
