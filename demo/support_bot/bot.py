"""Бот-автоответчик для заявок: работает на твоём железе или на сервере.

Что делает:
- отвечает на частые вопросы по шаблонам (цена, сроки, оплата, примеры),
- любое нестандартное сообщение пересылает тебе (или пишет в лог-файл),
- ведёт базу заявок в CSV,
- каждая заявка с упоминанием цены попадает в отдельный лог.

Никаких внешних сервисов: только токен бота.
"""
import csv
import os
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LEADS_CSV = os.environ.get("LEADS_CSV", "leads.csv")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # твой chat_id, туда шлём заявки

DEMO_URL = os.environ.get("DEMO_URL", "https://igor-dev-services-dgu5m087.agent.mira.tg")
REPO_URL = os.environ.get("REPO_URL", "https://github.com/ztfvpzz2ks-wq/igor-dev")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("support_bot")

PRICES = {
    "landing": 40,
    "bot": 60,
    "parser": 80,
    "bundle": 120,
}

REPLIES = {
    "price": (
        "Цены: лендинг от $40, Telegram-бот от $60, бот-парсер цен от $80, "
        "бот+лендинг от $120.\n"
        "Сроки 1-3 дня. Предоплата 50% (заказы до $120 - можно без неё)."
    ),
    "demo": (
        "Живое демо: " + DEMO_URL + "\n"
        "Код и примеры: " + REPO_URL
    ),
    "timeline": "Срок 1-3 дня: бот 2-3 дня, лендинг 1-2 дня. Исходники и инструкция передаю с заказом.",
    "payment": (
        "Предоплата 50%, остаток после приёмки. Заказы до $120 - можно без предоплаты. "
        "Правки после сдачи бесплатны, код остаётся вашим."
    ),
    "stack": "Пишу на Python (python-telegram-bot), лендинги - чистый HTML/CSS/JS. Код открытый, можете посмотреть до заказа.",
    "contact": (
        "На связи Игорь, отвечает в течение дня. Оставьте, пожалуйста, ваш контакт (телефон или Telegram) "
        "и коротко задачу - вернусь с ценой и сроком."
    ),
    "price_uk": "Ціни: лендинг від $40, Telegram-бот від $60, бот-парсер цін від $80, бот+лендинг від $120.\nТермін 1-3 дні. Передоплата 50% (замовлення до $120 - можна без неї).",
    "demo_uk": "Живе демо: " + DEMO_URL + "\nКод і приклади: " + REPO_URL,
    "timeline_uk": "Термін 1-3 дні: бот 2-3 дні, лендинг 1-2 дні. Вихідники та інструкція передаю разом із замовленням.",
    "payment_uk": "Передоплата 50%, решта після приймання. Замовлення до $120 - можна без передоплати. Правки після здачі безкоштовні, код залишається вашим.",
    "hello_uk": "Вітаю! Роблю Telegram-ботів та лендинги під ключ.\nНапишіть /price - ціни, /demo - приклади, /lead - залишити заявку.",
    "hello": (
        "Привет! Делаю Telegram-ботов и лендинги под ключ.\n"
        "Напишите /price - цены, /demo - примеры, /lead - оставить заявку."
    ),
}

KEYWORDS = {
    "hello": ["start", "начать", "старт", "привет", "здравствуй", "здрасте", "добрый", "hello", "hi", "hey"],
    "price": ["сколько стоит", "сколько будет стоить", "стоимость", "цена", "цены", "прайс",
              "тариф", "тарифы", "price", "cost", "how much", "pricing"],
    "demo": ["демо", "пример", "примеры", "посмотреть", "показать", "код", "github", "репозиторий",
             "работает ли", "demo", "example", "portfolio", "github"],
    "timeline": ["сколько дней", "срок", "сроки", "как быстро", "когда сделаете", "когда будет готово",
                 "сколько времени", "deadline", "how long", "timeline", "eta"],
    "payment": ["оплата", "оплатить", "предоплата", "как платить", "как оплатить", "способ оплаты",
                "перевод", "карта", "крипта", "payment", "prepay", "pay"],
    "stack": ["на чём написано", "на чем написано", "стек", "технолог", "язык", "python", "stack", "tech"],
    "contact": ["телефон", "телеграм", "telegram", "почта", "email", "связаться", "номер", "contact",
                "телефон", "залиште", "контакт", "зв'яжіться", "напишіть"],
    "price_uk": ["скільки це коштує", "скільки коштує", "скільки це", "вартість", "цена", "ціни",
                 "прайс", "тарифи", "скільки буде коштувати", "скільки варто"],
    "demo_uk": ["приклад", "приклади", "демо", "показати", "код", "github", "репозиторій", "працює",
                "приклад коду", "приклади робіт"],
    "timeline_uk": ["як довго", "скільки часу", "термін", "строки", "коли зможете", "коли буде готово"],
    "payment_uk": ["оплата", "оплатити", "передоплата", "як оплатити", "спосіб оплати", "переказ",
                   "картка", "крипта", "передоплата", "аванс"],
    "hello_uk": ["привіт", "привіт!", "вітаю", "добрий день", "доброго дня", "начати", "старт", "хай"],
}

LEAD_WORDS = ["потрібен", "потрібна", "потрібно", "хочу", "хотів", "замовляю", "зробіть", "зроби",
              "бюджет", "дорого", "знижка", "потрібна допомога","нужен", "нужна", "нужно", "хочу", "хотел", "заказать", "сделайте", "сделай", "сделать",
              "бюджет", "дорого", "скидк", "скидку", "почини", "доделай", "нужна помощь", "подскажите"]


@dataclass
class Lead:
    user_id: int
    name: str = ""
    contact: str = ""
    text: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    status: str = "new"


def save_lead(lead: Lead) -> None:
    is_new = not os.path.exists(LEADS_CSV)
    with open(LEADS_CSV, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if is_new:
            w.writerow(["created_at", "status", "user_id", "name", "contact", "text"])
        w.writerow([lead.created_at, lead.status, lead.user_id, lead.name, lead.contact, lead.text])


INCOMING_LOG = os.environ.get("INCOMING_LOG", "incoming.log")


def _log_update(update: Update) -> None:
    m = update.effective_message
    if m is None or m.text is None:
        return
    u = update.effective_user
    with open(INCOMING_LOG, "a", encoding="utf-8") as fh:
        fh.write("%s | chat_id=%s | user_id=%s | @%s | %s\n" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            update.effective_chat.id, u.id, u.username or "-", m.text.replace("\n", " ")))


def normalize(text: str) -> str:
    """Приводит текст к сравнимому виду: убирает ё/е, украинские і/ї/є -> и/е,
    схлопывает пробелы. Нужно, потому что 'стоїть' и 'стоит' — одно и то же."""
    t = text.lower().strip()
    t = t.replace("ё", "е").replace("Ё", "Е")
    t = t.replace("і", "и").replace("І", "И")
    t = t.replace("ї", "и").replace("Ї", "И")
    t = t.replace("є", "е").replace("Є", "Е")
    t = t.replace("ґ", "г").replace("Ґ", "Г")
    t = t.replace(";", ",").replace("!", " ").replace("?", " ")
    t = " ".join(t.split())
    return t


def detect(text: str) -> str:
    t = normalize(text)
    for key, words in KEYWORDS.items():
        for w in words:
            if normalize(w) in t:
                return key
    return ""


def looks_like_lead(text: str) -> bool:
    t = normalize(text)
    if detect(t) in ("hello", "hello_uk"):
        return False
    return any(normalize(w) in t for w in LEAD_WORDS)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _log_update(update)
    await update.message.reply_text(REPLIES["hello"])


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(REPLIES["price"])


async def cmd_demo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(REPLIES["demo"])


async def cmd_lead(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lead"] = Lead(user_id=update.effective_user.id, name=update.effective_user.first_name or "")
    await update.message.reply_text("Как вас зовут?")
    return 1


async def lead_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lead = context.user_data["lead"]
    lead.name = update.message.text.strip()
    await update.message.reply_text("Контакт для связи (Telegram, телефон или почта):")
    return 2


async def lead_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lead = context.user_data["lead"]
    lead.contact = update.message.text.strip()
    lead.text = "заявка через /lead"
    save_lead(lead)
    if ADMIN_ID:
        await context.bot.send_message(
            ADMIN_ID,
            "Новая заявка:\nИмя: %s\nКонтакт: %s\nСсылка: tg://user?id=%s"
            % (lead.name, lead.contact, lead.user_id),
        )
    await update.message.reply_text("Готово, заявка принята. Отвечу в течение дня.")
    return 3


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    _log_update(update)
    text = update.message.text or ""
    user = update.effective_user
    key = detect(text)

    if key:
        await update.message.reply_text(REPLIES[key])
        return

    if looks_like_lead(text):
        lead = Lead(user_id=user.id, name=user.first_name or "", contact=user.username or "", text=text)
        save_lead(lead)
        if ADMIN_ID:
            await context.bot.send_message(
                ADMIN_ID,
                "Похоже на заявку:\n%s\nКонтакт: %s\nСсылка: tg://user?id=%s"
                % (text, lead.contact or "не указан", user.id),
            )
        await update.message.reply_text(
            "Принял. Уточните, пожалуйста: что должно происходить (словами), "
            "где будет жить и к какому сроку. Сразу скажу цену и срок."
        )
        return

    log.info("unhandled from %s: %s", user.id, text)
    await update.message.reply_text(
        "Уточню у мастера и вернусь с ответом.\n"
        "Пока вот главное: /price - цены, /demo - примеры."
    )


async def on_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.info("non-text from %s", update.effective_user.id)


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("demo", cmd_demo))
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("lead", cmd_lead)],
            states={
                1: [MessageHandler(filters.TEXT & ~filters.COMMAND, lead_name)],
                2: [MessageHandler(filters.TEXT & ~filters.COMMAND, lead_contact)],
            },
            fallbacks=[CommandHandler("cancel", lambda u, c: u.message.reply_text("Отменил."))],
        )
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    app.add_handler(MessageHandler(~filters.TEXT & ~filters.COMMAND, on_unknown))
    app.run_polling()
    log.info("bot started")


if __name__ == "__main__":
    main()
