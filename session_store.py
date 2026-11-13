from collections import defaultdict
from config import MAX_HISTORY

_history: dict[int, list[dict]] = defaultdict(list)
_seen_updates: set[int] = set()


def get_history(chat_id: int) -> list[dict]:
    return _history[chat_id]


def append(chat_id: int, role: str, content: str) -> None:
    _history[chat_id].append({"role": role, "content": content})
    if len(_history[chat_id]) > MAX_HISTORY:
        _history[chat_id][:] = _history[chat_id][-MAX_HISTORY:]


def pop_last(chat_id: int) -> None:
    if _history[chat_id]:
        _history[chat_id].pop()


def reset(chat_id: int) -> None:
    _history.pop(chat_id, None)


def is_duplicate(update_id: int) -> bool:
    if update_id in _seen_updates:
        return True
    _seen_updates.add(update_id)
    # держим множество небольшим
    if len(_seen_updates) > 1000:
        _seen_updates.clear()
        _seen_updates.add(update_id)
    return False
