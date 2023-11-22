from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot
from dotenv import load_dotenv
from jess import Jess
import os
import asyncio
import requests

load_dotenv()

chat_id = os.getenv('TELEGRAM_CHAT_ID')
telegram_token = os.getenv('TELEGRAM_TOKEN')

async def start(update, context):
    await update.message.reply_text('Hello! I am your bot.')

async def message(update, context):
    jess.send_message(update.message.text)

async def get_chat_id(update, context):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

def message_handler(meesage_to_send):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={meesage_to_send}"
    return requests.get(url).json()


bot = Bot(token=telegram_token)
jess = Jess.start(message_handler)

def main():
    print("starting")
    application = Application.builder().bot(bot).build()
    start_handler = CommandHandler('start', start)
    start_handler = CommandHandler('get_chat_id', get_chat_id)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT, message)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
