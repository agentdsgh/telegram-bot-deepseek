import logging
import time
import requests
from config import DEEPSEEK_URL, DEEPSEEK_KEY, DEFAULT_MODEL
from session_store import get_history, append, pop_last

logger = logging.getLogger(__name__)

# сколько раз пробуем достучаться до прокси при сетевых ошибках
MAX_RETRIES = int(__import__("os").environ.get("DEEPSEEK_MAX_RETRIES", "3"))
# базовая пауза между попытками (сек), растёт экспоненциально: 6, 18, 30
RETRY_BASE_DELAY = float(__import__("os").environ.get("DEEPSEEK_RETRY_BASE_DELAY", "6"))


class DeepSeekError(Exception):
    pass


def _post_with_retry(payload: dict, headers: dict) -> requests.Response:
    """POST к прокси с retry только на сетевые ошибки (ConnectionError/Timeout)."""
    last_exc: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=180)
        except (requests.ConnectionError, requests.Timeout) as e:
            last_exc = e
            if attempt == MAX_RETRIES:
                break
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "proxy unavailable (attempt %d/%d), retry in %.1fs: %s",
                attempt, MAX_RETRIES, delay, e,
            )
            time.sleep(delay)
    # сюда попадаем, только если все попытки провалились
    raise last_exc  # type: ignore[misc]


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
        r = _post_with_retry(payload, headers)
    except requests.Timeout:
        pop_last(chat_id)
        raise DeepSeekError("Превышено время ожидания ответа от модели.")
    except requests.RequestException as e:
        pop_last(chat_id)
        raise DeepSeekError(f"Прокси недоступен: {e}")

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
