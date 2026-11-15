# Демо: лендинг -> бот -> таблица

Связка целиком: форма на лендинге отправляет заявку на локальный сервер, тот пишет её в CSV и дублирует в Telegram.

## Запуск

```bash
pip install -r requirements.txt
export LEADS_CSV=leads.csv
export TELEGRAM_BOT_TOKEN=123456:ABC-your-token
export TELEGRAM_CHAT_ID=000000000
python server.py
```

## Проверка

```bash
curl -X POST http://127.0.0.1:8000/lead \
  -H "Content-Type: application/json" \
  -d '{"name":"Ivan","contact":"@ivan","comment":"Nuzhen bot"}'
```

Заявка появится в `leads.csv` и в Telegram.

## Подключение к лендингу

В `../landing_template/index.html` замените `BOT_TOKEN` и `CHAT_ID` на свои, а `fetch` — на адрес вашего сервера с путём `/lead`.

## Файлы

- `server.py` — приём заявок, CSV, уведомление в Telegram
- `requirements.txt` — зависимости
- `leads.csv` — база заявок (создаётся автоматически)
