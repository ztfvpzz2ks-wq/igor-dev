# Case Study 5 — Telegram Lead Bot with Admin Panel

**Source:** https://github.com/ztfvpzz2ks-wq/igor-dev/tree/main/case5_admin_panel

## Title (Upwork)

Telegram Lead Bot with Web Admin Panel — capture requests, manage status, export CSV

## Short description

A Telegram bot that captures customer requests in free-form text and a lightweight web panel where you manage them: search, status changes, CSV export. Pure Python standard library — no framework, no hosting headaches.

## Full description

I will build a **Telegram bot with a web admin panel** that turns scattered messages into an organized pipeline of leads.

### The problem it solves

Requests rarely arrive in a neat form. A customer writes: *"need a bot for appointments, telegram @ivan"*. Strict forms with mandatory fields lose exactly those leads. This bot takes the free-form message, extracts the contact and the service type automatically, and files it where you can actually work with it.

### Bot features

- **Free-form intake** — the customer types naturally, no buttons or required fields
- **Automatic service detection** — recognises landing page / Telegram bot / price parser / admin panel from the message text
- **Automatic contact extraction** — @username, phone number or URL
- **Ukrainian + Russian** — Ukrainian letters (і, ї, є, ґ) are normalised, so Ukrainian requests are understood correctly
- **Instant admin notification** — the lead lands in your Telegram the moment it arrives, with service, contact and full text
- **Smart reply** — the bot asks for a contact if one is missing instead of losing the request

### Admin panel features

- **Full list of leads** with date, name, contact, service and status
- **Search** across all fields
- **Filter by status**
- **Change status inline** from the table: `new` → `in_progress` → `done` / `rejected`
- **CSV export** for Excel, CRM import or accounting
- **Optional access token** — API and CSV export are protected; the panel is open only if you leave the token unset
- **Zero data loss** — writes go through a temp file and atomic replace, so a restart never corrupts data

### Tech

Pure Python 3.9+ standard library only. No pip install, no framework, no database server — the panel and the bot share one JSON file. That means you can deploy it in a minute on any VPS, or hand it to your host without a Docker container.

```bash
# panel
export ADMIN_TOKEN=change-me
export ADMIN_PORT=8080
python3 panel.py

# bot
export TG_TOKEN=123:ABC
export ADMIN_CHAT_ID=your_chat_id
export LEADS_FILE=leads.json
python3 bot.py
```

I can additionally set up nginx + HTTPS, a systemd service and a domain, or package it as a Docker image if you prefer.

### Ideal for

- Service businesses taking requests via Telegram (repair, beauty, tutoring, moving, web services)
- Freelancers and small studios who keep leads in their personal chat
- Anyone who has lost a request because it was buried in a chat

### Price and delivery

- **Fixed price: $120–200** depending on custom fields, extra services, auth and deployment
- **Delivery: 3–5 days**
- 50% upfront, 50% on delivery
- One round of revisions included, plus a week of support

### Questions

Message me with what your business needs — I will tell you honestly if a simpler solution is enough.
