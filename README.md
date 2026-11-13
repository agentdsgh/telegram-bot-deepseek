# DeepSeek Telegram Bot

Минимальный Telegram-бот (webhook) для FreeDeepseekAPI.

## Переменные окружения
- TELEGRAM_BOT_TOKEN — токен от @BotFather
- DEEPSEEK_API_URL — http://<service>.railway.internal:8080/v1/chat/completions
- DEEPSEEK_API_KEY — если у прокси задан PROXY_API_KEY
- WEBHOOK_SECRET — любой случайный секрет (рекомендуется)
- RAILWAY_PUBLIC_DOMAIN — Railway проставляет автоматически

## Запуск
python main.py
