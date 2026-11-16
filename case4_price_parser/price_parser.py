"""Кейс 4: бот-парсер цен.

Следит за источником цен (JSON API биржи или свой endpoint) и присылает в Telegram
уведомление, когда цена изменилась сильнее порога.

Поддерживает форматы: CoinGecko, Coinbase, Kraken, Gemini, Gate.io, OKX, Bitfinex,
а также свой {"price": 123.45}.

Бот НЕ использует getUpdates: он только отправляет уведомления, поэтому может
работать на том же токене, что и основной бот, без конфликта.

Запуск:
    export TG_TOKEN=123:ABC
    export TG_CHAT_ID=7409753745
    export SOURCE_URL=https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
    export THRESHOLD=0.5     # процентов
    export POLL_SEC=60
    python3 price_parser.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

TG_TOKEN = os.environ.get("TG_TOKEN", "")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID", "")
SOURCE_URL = os.environ.get("SOURCE_URL", "")
THRESHOLD = float(os.environ.get("THRESHOLD", "0.5"))
POLL_SEC = int(os.environ.get("POLL_SEC", "60"))
STATE_FILE = os.environ.get("STATE_FILE", "last_price.json")

# Ключи, которые НЕ являются ценой: метаданные, объёмы, таймстемпы
SKIP_KEYS = {
    "timestamp", "time", "volume", "volumes", "bid", "ask", "bidpx", "askpx",
    "base_volume", "quote_volume", "count", "open", "open24h", "open_interest",
    "size", "qty", "quantity", "high", "low", "high24h", "low24h", "change",
    "change_percentage", "volccy24h", "volbase24h", "base", "currency", "instid",
    "insttype", "currency_pair", "symbol", "pair", "code", "error", "errors",
    "lowest_ask", "lowest_size", "highest_bid", "highest_size", "lastsz",
    "asksz", "bidsz", "asks", "bids", "mark", "index", "openinterest", "delta",
    "timestampms", "nonce", "hash", "method", "ch", "vwap",
}

# Приоритетные ключи с ценой
PRICE_KEYS = ("price", "amount", "last", "close", "usd", "usdt", "eur", "btc", "c", "p", "o")


def _to_float(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    return None


def _from_list(node):
    """Список пар вида ["65097", "2.6", ...] (Bitfinex): первый элемент - цена."""
    if not node or not isinstance(node, list):
        return None
    return _to_float(node[0])


def _find_price(node):
    """Ищет цену в произвольном JSON разных бирж:
    {"price": x} | {"data":{"amount": x}} (Coinbase) | {"bitcoin":{"usd": x}} (CoinGecko)
    | {"result":{"XBT":{"c":["65038.1", ...]}}} (Kraken) | [{"last": x}] (Gate.io/OKX)
    | [65097, 2.6, ...] (Bitfinex) | {"last": x} (Gemini)
    """
    if isinstance(node, dict):
        for k in PRICE_KEYS:
            if k in node:
                got = _to_float(node[k])
                if got is not None:
                    return got
                if isinstance(node[k], list):
                    got = _from_list(node[k])
                    if got is not None:
                        return got
        for k, v in node.items():
            if k in SKIP_KEYS:
                continue
            got = _find_price(v)
            if got is not None:
                return got
    elif isinstance(node, list):
        got = _from_list(node)
        if got is not None:
            return got
        for item in node:
            got = _find_price(item)
            if got is not None:
                return got
    return None


def fetch_price(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    price = _find_price(data)
    if price is None:
        raise ValueError("price not found in response")
    return price


def send_message(text: str) -> bool:
    """Отправка в Telegram напрямую через Bot API - без getUpdates."""
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": TG_CHAT_ID, "text": text}).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")).get("ok", False)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        print("send failed:", exc)
        return False


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (ValueError, OSError):
            return {}
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def check_once(state):
    """Одна проверка. Возвращает обновлённое состояние."""
    price = fetch_price(SOURCE_URL)
    last = state.get("price")

    if last is not None:
        change = (price - last) / last * 100
        if abs(change) >= THRESHOLD:
            arrow = "\u2b07" if change > 0 else "\u2b06"
            send_message(
                f"{arrow} Цена изменилась: {last:.2f} -> {price:.2f} ({change:+.2f}%)"
            )
        state["price"] = price
    else:
        state["price"] = price
        send_message(
            f"Парсер запущен. Бот следит за ценой. Текущая цена: {price:.2f}"
        )
    save_state(state)
    return state


def main():
    if not TG_TOKEN or not TG_CHAT_ID or not SOURCE_URL:
        print("Нужны переменные TG_TOKEN, TG_CHAT_ID, SOURCE_URL")
        sys.exit(1)

    state = load_state()
    while True:
        try:
            state = check_once(state)
        except Exception as exc:
            print("check failed:", exc)
        time.sleep(POLL_SEC)


if __name__ == "__main__":
    main()
