"""Telegram-бот приёма заявок.

Заявки складываются в CSV. Без внешней базы — файл и есть база.
"""
import csv
import os
import logging
from dataclasses import dataclass, field
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
LEADS_CSV = os.environ.get("LEADS_CSV", "leads.csv")

NAME, CONTACT, COMMENT = range(3)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("leadbot")


@dataclass
class Lead:
    name: str = ""
    contact: str = ""
    comment: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


def save_lead(lead: Lead) -> None:
    is_new = not os.path.exists(LEADS_CSV)
    with open(LEADS_CSV, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if is_new:
            writer.writerow(["created_at", "name", "contact", "comment"])
        writer.writerow([lead.created_at, lead.name, lead.contact, lead.comment])


def read_leads(limit: int = 10):
    if not os.path.exists(LEADS_CSV):
        return []
    with open(LEADS_CSV, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return rows[-limit:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот приёма заявок.\n"
        "Напишите /lead — и я спрошу имя, контакт и комментарий.\n"
        "Все заявки сохраняются в таблицу."
    )


async def lead_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lead"] = Lead()
    await update.message.reply_text("Как вас зовут?")
    return NAME


async def lead_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lead"].name = update.message.text.strip()
    await update.message.reply_text("Какой контакт? Telegram, телефон или почта:")
    return CONTACT


async def lead_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lead"].contact = update.message.text.strip()
    await update.message.reply_text("Комментарий (можно прочерк, если не важно):")
    return COMMENT


async def lead_comment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lead = context.user_data["lead"]
    lead.comment = update.message.text.strip()
    save_lead(lead)
    log.info("saved lead: %s", lead.contact)
    await update.message.reply_text(
        "Готово, заявка принята.\nИмя: %s\nКонтакт: %s" % (lead.name, lead.contact)
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Ок, отменил. Напишите /lead, если понадобится.")
    return ConversationHandler.END


async def show_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    leads = read_leads()
    if not leads:
        await update.message.reply_text("Заявок пока нет.")
        return
    lines = []
    for i, lead in enumerate(leads, 1):
        lines.append("%d. %s — %s (%s)" % (i, lead["created_at"], lead["name"], lead["contact"]))
    await update.message.reply_text("Последние заявки:\n" + "\n".join(lines))


def main() -> None:
    app = ApplicationBuilder().token(TOKEN).build()

    lead_flow = ConversationHandler(
        entry_points=[CommandHandler("lead", lead_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, lead_name)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lead_contact)],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, lead_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", show_list))
    app.add_handler(lead_flow)
    app.run_polling()


if __name__ == "__main__":
    main()
