run-api:
	PROJECT_NAME=memo nohup poetry run python api.py > api.log 2>&1 &

run-tg-bot:
	PYTHONPATH=/home/admin/projects/memos/src PROJECT_NAME=memo nohup poetry run python src/clients/telegram_client/bot.py > bot.log 2>&1 &

show-processes:
	ps aux | grep [m]emo

run: run-api run-tg-bot
