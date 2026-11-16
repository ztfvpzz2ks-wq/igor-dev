# Отклик 1 — Telegram-бот (заявки / лиды / админ-панель)

**Когда применять:** вакансия ищет бота, который принимает заявки, отвечает клиентам, ведёт базу, парсит сообщения, делает рассылки, работает с заказами.

Hi [Name],

I build exactly this — Telegram bots that take requests in free form and turn them into a structured list, instead of another form nobody fills in.

The version I built most recently does this: a client writes "need a bot for appointments, telegram @ivan" and the bot itself works out that it is a bot request, pulls out the contact, files it, and notifies the owner right away. On top of that there is a small web panel — list, search, filter by status, change status inline, export to CSV. Pure Python standard library, so there is nothing to install and no database server to pay for.

The code is public, so you can judge it before we start:
https://github.com/ztfvpzz2ks-wq/igor-dev/tree/main/case5_admin_panel

It handles Ukrainian and Russian input, including Ukrainian letters (і, ї, є, ґ), which matters if your customers write that way.

Two questions so I can quote you the right number:
1. Do you want the bot to only collect requests, or also reply to the customer automatically?
2. Do you need the web panel, or is a spreadsheet of requests enough?

I can send you a working demo of the flow before we agree anything, so you can judge the result and not just the description.

[Name], what would be the deadline on your side?

Igor
Telegram: https://t.me/mira?start=ref_7409753745
