# Трекер заявок

Одна таблица вместо заметок: все заявки из чатов в одном CSV, который открывается в Excel или Google Sheets.

## Использование

```bash
python tracker.py add --name "Иван" --contact "@ivan" --service bot --note "нужен парсер цен" --price 80
python tracker.py list
python tracker.py find ivan
python tracker.py status @ivan done --paid yes --price 80
python tracker.py stats
```

## Статусы

`new` -> `in_progress` -> `waiting` -> `done`, либо `declined`.

## Файл

`leads.csv` — сама база (создаётся автоматически в рабочей папке).
