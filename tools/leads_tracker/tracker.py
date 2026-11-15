"""Трекер заявок из Telegram-чатов: одна таблица вместо заметок.

Простой CSV, который можно открыть в Excel/Google Sheets.
Скрипт добавляет заявку, показывает все или ищет по имени/контакту.

Использование:
    python tracker.py add --name "Иван" --contact "@ivan" --service "bot" --note "нужен парсер цен" --price 80
    python tracker.py list
    python tracker.py find ivan
    python tracker.py stats
"""
import argparse
import csv
import os
from datetime import datetime

CSV_PATH = os.environ.get("LEADS_CSV", "leads.csv")
FIELDS = ["created_at", "status", "name", "contact", "service", "note", "price_usd", "paid"]


def load():
    if not os.path.exists(CSV_PATH):
        return []
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def save(rows):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def add(a):
    rows = load()
    rows.append({
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "new",
        "name": a.name,
        "contact": a.contact,
        "service": a.service,
        "note": a.note,
        "price_usd": a.price,
        "paid": "no",
    })
    save(rows)
    print("Заявка добавлена: %s (%s), %s" % (a.name, a.contact, a.service))


def set_status(contact, status, price=None, paid=None):
    rows = load()
    found = False
    for r in rows:
        if contact.lower() in (r["contact"] + " " + r["name"]).lower():
            r["status"] = status
            if price is not None:
                r["price_usd"] = str(price)
            if paid is not None:
                r["paid"] = paid
            found = True
    if found:
        save(rows)
    print("Обновлено" if found else "Не найдено: " + contact)


def listing():
    rows = load()
    if not rows:
        print("Заявок нет.")
        return
    for r in rows:
        print("%s | %-8s | %-12s | %-10s | $%s | %s" % (
            r["created_at"], r["status"], r["name"], r["contact"], r["price_usd"], r["note"]))


def find(q):
    for r in load():
        if q.lower() in (r["contact"] + " " + r["name"] + " " + r["note"]).lower():
            print(r)


def stats():
    rows = load()
    income = sum(float(r["price_usd"] or 0) for r in rows if r["paid"] == "yes")
    open_sum = sum(float(r["price_usd"] or 0) for r in rows if r["status"] != "done" and r["paid"] != "yes")
    print("Всего заявок: %d" % len(rows))
    print("Заработано (оплачено): $%.0f" % income)
    print("В работе / ждут оплаты: $%.0f" % open_sum)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--name", required=True)
    a.add_argument("--contact", required=True)
    a.add_argument("--service", default="bot")
    a.add_argument("--note", default="")
    a.add_argument("--price", default="0")
    s = sub.add_parser("status")
    s.add_argument("contact")
    s.add_argument("status", choices=["new", "in_progress", "waiting", "done", "declined"])
    s.add_argument("--price")
    s.add_argument("--paid", choices=["yes", "no"])
    sub.add_parser("list")
    f = sub.add_parser("find")
    f.add_argument("query")
    sub.add_parser("stats")
    args = p.parse_args()
    {"add": lambda: add(args), "status": lambda: set_status(args.contact, args.status, args.price, args.paid),
     "list": listing, "find": lambda: find(args.query), "stats": stats}[args.cmd]()
