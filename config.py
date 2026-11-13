import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
DEEPSEEK_URL = os.environ.get(
    "DEEPSEEK_API_URL",
    "http://127.0.0.1:8080/v1/chat/completions",
)
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEFAULT_MODEL = os.environ.get("DEFAULT_MODEL", "deepseek-chat")
MAX_HISTORY = int(os.environ.get("MAX_HISTORY", "20"))
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
PORT = int(os.environ.get("PORT", "8080"))
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
