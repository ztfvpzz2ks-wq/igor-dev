#!/bin/bash
export TG_TOKEN="7741197519:AAGIBpD12ka7jYPoV8KurVUWxX7ptmgsJgs"
export TG_CHAT_ID="7409753745"
export SOURCE_URL="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
export THRESHOLD="0.15"
export POLL_SEC="90"
export STATE_FILE="/mnt/files/work/portfolio2/case4_price_parser/last_price.json"
exec bash "/mnt/files/work/portfolio2/case4_price_parser/supervisor.sh"
