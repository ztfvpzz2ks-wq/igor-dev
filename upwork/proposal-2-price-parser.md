# Отклик 2 — Парсер цен / мониторинг / алерты

**Когда применять:** вакансия про scraping цен, мониторинг сайта, отслеживание изменений, уведомления, алерты, парсинг API.

Hi [Name],

I have already built the thing you are describing, so let me be specific rather than theoretical.

A Python script that watches a price across seven exchanges — Coinbase, Kraken, CoinGecko, Gemini, Gate.io, OKX, Bitfinex — and sends you a Telegram alert when the move passes your threshold. The tricky part is that every exchange nests its price data differently; that part is already solved. Your threshold, your source, your polling interval. State survives a restart, and there is a supervisor script that brings it back if it dies.

Code is public: https://github.com/ztfvpzz2ks-wq/igor-dev/tree/main/case4_price_parser

If your case is not crypto — a product price on a site, a rate, an auction bid — the same structure works, I just add the source adapter.

Two things that change the price:
1. How many sources do you need, and are they JSON APIs or HTML pages?
2. Do you want a Telegram alert only, or also a history file / CSV of every change?

I can send a working demo on your own source before we start, so you are buying a result, not a promise.

[Name], what is the source URL you want it to watch?

Igor
Telegram: https://t.me/mira?start=ref_7409753745
