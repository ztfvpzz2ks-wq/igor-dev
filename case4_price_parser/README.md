# Кейс 4 — бот-парсер цен

Следит за источником цен и присылает уведомление в Telegram, когда цена изменилась
сильнее заданного порога.

## Что умеет
- Любой JSON-источник: своя ручка `{"price": 123.45}` или готовая биржа
- Готовые адаптеры: CoinGecko, Coinbase, Kraken, Gemini, Gate.io, OKX, Bitfinex
  — цена достаётся автоматически, метаданные (timestamp, volume, bid/ask) игнорируются
- Порог изменения (по умолчанию 0.5%)
- Уведомление со стрелкой и процентом изменения
- Состояние переживает перезапуск (`last_price.json`)
- Авторестарт: `supervisor.sh` поднимает бота, если он упал
- **Без внешних зависимостей** — чистая стандартная библиотека Python 3
- Бот только отправляет сообщения, поэтому работает на том же токене,
  что и основной бот, без конфликта `getUpdates`

## Запуск
```bash
export TG_TOKEN=123:ABC
export TG_CHAT_ID=7409753745
export SOURCE_URL=https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
export THRESHOLD=0.5
export POLL_SEC=60
python3 price_parser.py
```

Или под супервизором (в фоне, с авторестартом):
```bash
nohup ./run.sh &
```

## Для клиента
Достаточно дать ссылку на источник и сказать, какой процент считать «значимым».
Если источник отдаёт нестандартный JSON — поправлю парсер под него за минуты.

## Примеры источников
| Биржа | Ссылка |
|---|---|
| CoinGecko | `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd` |
| Coinbase | `https://api.coinbase.com/v2/prices/BTC-USD/spot` |
| Kraken | `https://api.kraken.com/0/public/Ticker?pair=XBTUSD` |
| Gemini | `https://api.gemini.com/v1/pubticker/btcusd` |
| Gate.io | `https://api.gateio.ws/api/v4/spot/tickers?currency_pair=BTC_USDT` |
| OKX | `https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT` |
| Bitfinex | `https://api.bitfinex.com/v2/ticker/tBTCUSD` |
