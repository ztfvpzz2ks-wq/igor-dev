# Case Study 4 — Crypto Price Parser Bot

**Source:** https://github.com/ztfvpzz2ks-wq/igor-dev/tree/main/case4_price_parser

## Title (Upwork)

Crypto Price Parser Bot — multi-exchange price monitor with Telegram alerts

## Short description

A Python bot that watches crypto prices across 7 exchanges and sends you a Telegram alert the moment the price moves past your threshold. Runs on any VPS or Raspberry Pi. Zero heavy dependencies, you own the code.

## Full description

I will build a **crypto price parser bot** that monitors price changes across the exchanges you choose and pushes notifications straight to your Telegram chat.

### What you get

- **7 exchange sources supported out of the box:** Coinbase, Kraken, CoinGecko, Gemini, Gate.io, OKX, Bitfinex
- **Any custom JSON endpoint** — if your price comes from a different API, it is a one-line config change
- **Configurable alert threshold** (e.g. alert on any move above 0.15%)
- **Telegram notifications** sent directly through the Bot API — no polling conflicts, so it can run alongside your other bot on the same token
- **State persistence** so the bot remembers the last price across restarts and does not spam you on startup
- **Clean, documented Python** — commented, structured, easy for you to modify or extend
- **README** with the full table of sources, environment variables and run commands

### How it works

The parser reads a JSON price endpoint, finds the price inside the response regardless of the exchange structure, compares it against the last known value, and sends a Telegram message if the change exceeds your threshold. The tricky part — every exchange nests price data differently — is already solved and handled.

### Deployment

Runs on any Linux VPS, Raspberry Pi, or even a local machine:

```bash
export TG_TOKEN=123:ABC
export TG_CHAT_ID=your_chat_id
export SOURCE_URL=https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
export THRESHOLD=0.15
export POLL_SEC=60
python3 price_parser.py
```

I can also add a systemd service with auto-restart so it survives reboots.

### Ideal for

- Traders who want a price alert without watching a screen
- Shops or services that track a coin price
- Anyone who needs a small, reliable monitoring script

### Price and delivery

- **Fixed price: $60–120** depending on number of sources, extra alert rules and bot features
- **Delivery: 2–4 days**
- 50% upfront, 50% on delivery
- Unlimited revisions during the first week

### Questions

Ask me anything before ordering — I reply the same day.
