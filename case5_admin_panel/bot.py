"""Кейс 5: бот заявок - приём заявок и уведомление админа.

Только стандартная библиотека и Bot API напрямую. Этот файл не использует
getUpdates - он только разбирает входящий текст, чтобы работал в одном
процессе с основным ботом.

Переменные:
    TG_TOKEN       - токен бота
    ADMIN_CHAT_ID  - чат админа, туда приходят заявки
    LEADS_FILE     - общий JSON-файл с панелью
"""
import json
import os
import time
import urllib.error
import urllib.request

TG_TOKEN = os.environ.get("TG_TOKEN", "")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID", "")
LEADS_FILE = os.environ.get("LEADS_FILE", "leads.json")

SERVICES = ("лендинг", "телеграм-бот", "парсер цен", "админ-панель", "бот", "другое")


def normalize(text):
    """Приводит украинские буквы к русским и убирает лишние пробелы."""
    table = str.maketrans({
        "\u0456": "\u0438", "\u0457": "\u0438", "\u0454": "\u0435", "\u0491": "\u0433",
        "\u0406": "\u0418", "\u0407": "\u0418", "\u0404": "\u0415", "\u0490": "\u0413",
    })
    return " ".join(text.translate(table).lower().split())


def detect_service(text):
    t = normalize(text)
    for svc in SERVICES:
        if svc in t:
            return svc
    return "другое"


def extract_contact(text):
    for token in text.split():
        if "@" in token and len(token) > 2:
            return token
        if token.startswith("+") and len(token.replace("+", "").replace(" ", "")) >= 10:
            return token
        if token.startswith("http"):
            return token
    return ""


def load_leads():
    if not os.path.exists(LEADS_FILE):
        return []
    try:
        with open(LEADS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return []


def save_leads(leads):
    tmp = LEADS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    os.replace(tmp, LEADS_FILE)


def send_message(chat_id, text):
    url = "https://api.telegram.org/bot%s/sendMessage" % TG_TOKEN
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")).get("ok", False)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print("send failed:", exc)
        return False


def handle_message(text, user_name=""):
    """Разбирает текст заявки и сохраняет её. Возвращает ответ клиенту."""
    if normalize(text) in ("start", "начать", "/start", "привет", "hello", "hi"):
        return ("Привет! Опиши задачу одной строкой: что нужно сделать и как "
                "с тобой связаться (телефон, @юзерник или ссылка).\n"
                "Например: «нужен лендинг под услугу, @igor_dev».")

    contact = extract_contact(text)
    if not contact:
        return ("Понял задачу. Оставь, пожалуйста, контакт — @юзерник, телефон "
                "или ссылку.")

    leads = load_leads()
    lead = {
        "id": int(time.time() * 1000),
        "created_at": time.strftime("%Y-%m-%d %H:%M"),
        "name": user_name or text[:40],
        "contact": contact,
        "service": detect_service(text),
        "text": text[:500],
        "source": "telegram",
        "status": "new",
    }
    leads.insert(0, lead)
    save_leads(leads)

    if ADMIN_CHAT_ID:
        send_message(ADMIN_CHAT_ID,
                     "Новая заявка\nУслуга: %s\nКонтакт: %s\nТекст: %s"
                     % (lead["service"], lead["contact"], lead["text"]))
    return "Заявка принята, свяжемся в течение дня. Если срочно - напишите в Telegram."


def main():
    if not TG_TOKEN:
        print("Нужен TG_TOKEN")
        return
    print("Бот заявок готов. Обработчик: handle_message(text, user_name).")


if __name__ == "__main__":
    main()
