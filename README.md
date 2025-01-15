### This project provides voice memo storage.

#### Setup

The project dependencies and virtualenvs are managed by poetry.
First, create a virtualenv:

```shell
poerty env use python
```

Then install the dependencies:

```shell
poetry install
```

#### How to run

Main business logic is behind fastAPI. In order to run it execute:

```
poetry run python api.py
```

Client to the api are meant to be swappable, but right now there is only telegram bot. To run it:

```shell
cd src/clients/telegram_client
poetry run python bot.py
```

To run on the Pi:

```shell
PROJECT_NAME=memo nohup poetry run python api.py > api.log 2>&1 &
```

and

```shell
PYTHONPATH=/home/admin/projects/memos/src PROJECT_NAME=memo nohup poetry run python src/clients/telegram_client/bot.py > bot.log 2>&1 &
```

To see processes related to the project:

```shell
ps aux | grep [m]emo
```