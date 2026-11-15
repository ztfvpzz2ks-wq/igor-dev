"""Приём заявок с лендинга: POST JSON -> CSV + уведомление в Telegram.

Запуск:
    pip install -r requirements.txt
    export LEADS_CSV=leads.csv
    export TELEGRAM_BOT_TOKEN=123456:ABC-your-token
    export TELEGRAM_CHAT_ID=000000000
    python server.py
"""
import csv
import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests

LEADS_CSV = os.environ.get("LEADS_CSV", "leads.csv")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
PORT = int(os.environ.get("PORT", "8000"))


def save_lead(data: dict) -> None:
    is_new = not os.path.exists(LEADS_CSV)
    with open(LEADS_CSV, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if is_new:
            writer.writerow(["created_at", "name", "contact", "comment"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data.get("name", ""),
            data.get("contact", ""),
            data.get("comment", ""),
        ])


def notify_telegram(data: dict) -> None:
    if not BOT_TOKEN or not CHAT_ID:
        return
    text = "\n".join([
        "Новая заявка с сайта",
        "Имя: %s" % data.get("name", ""),
        "Контакт: %s" % data.get("contact", ""),
        "Комментарий: %s" % (data.get("comment") or "—"),
    ])
    try:
        requests.post(
            "https://api.telegram.org/bot%s/sendMessage" % BOT_TOKEN,
            json={"chat_id": CHAT_ID, "text": text},
            timeout=10,
        )
    except requests.RequestException as exc:
        print("Не удалось отправить в Telegram: %s" % exc)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/lead":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(raw)
        except ValueError:
            self.send_error(400, "Bad JSON")
            return

        save_lead(data)
        notify_telegram(data)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


if __name__ == "__main__":
    print("Leads server on http://127.0.0.1:%s" % PORT)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
