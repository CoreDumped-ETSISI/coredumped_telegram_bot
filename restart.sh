#!/bin/bash
cd /home/admin/core_dumped_telegram_bot/ &&
screen -X -S CDumpedBot quit
screen -dmS CDumpedBot python /home/admin/core_dumped_telegram_bot/core_dumped_bot_with_python_telegram_bot.py
