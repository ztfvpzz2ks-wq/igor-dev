#!/bin/bash
# Авторестарт парсера цен: поднимает заново, если процесс упал.
cd "$(dirname "$0")" || exit 1
while true; do
    python3 price_parser.py >> parser.log 2>&1
    echo "$(date '+%F %T') parser exited, restarting in 5s" >> parser.log
    sleep 5
done
