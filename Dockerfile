FROM python:3.8-slim

WORKDIR /app

COPY .env /app/.env

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "./telegram_bot.py"]