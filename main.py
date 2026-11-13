import json
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from config import PORT, WEBHOOK_PATH, WEBHOOK_SECRET, LOG_LEVEL
from telegram_api import set_webhook
from handlers import handle_update
from session_store import is_duplicate

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        if self.path != WEBHOOK_PATH:
            self.send_response(404)
            self.end_headers()
            return

        # защита от поддельных запросов
        if WEBHOOK_SECRET:
            if self.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        # отвечаем Telegram сразу, чтобы он не повторял запрос
        self.send_response(200)
        self.end_headers()

        try:
            update = json.loads(body)
        except ValueError:
            logger.warning("bad json from telegram")
            return

        update_id = update.get("update_id")
        if update_id is not None and is_duplicate(update_id):
            logger.info("duplicate update_id=%s skipped", update_id)
            return

        try:
            handle_update(update)
        except Exception:
            logger.exception("handle_update failed")

    def log_message(self, fmt, *args):
        # отключаем стандартный шумный лог http.server
        pass


def main():
    import os
    public_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
    if public_domain:
        set_webhook(f"https://{public_domain}{WEBHOOK_PATH}", WEBHOOK_SECRET)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), WebhookHandler)
    logger.info("webhook server on port %s", PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()
