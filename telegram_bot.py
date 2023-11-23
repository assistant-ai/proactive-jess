from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot
from dotenv import load_dotenv
from jess import Jess
from extensions import get_extensions
import os
import requests

load_dotenv()

chat_id = os.getenv('TELEGRAM_CHAT_ID')
telegram_token = os.getenv('TELEGRAM_TOKEN')

async def start(update, context):
    await update.message.reply_text('Hello! I am your bot.')

async def message(update, context):
    if str(update.message.chat_id) != str(chat_id):
        return
    jess.send_message(update.message.text)

async def get_chat_id(update, context):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

async def drop_chat(update, context):
    jess.drop_chat_thread()
    await update.message.reply_text("done")

def message_handler(meesage_to_send):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={meesage_to_send}"
    return requests.get(url).json()


bot = Bot(token=telegram_token)
jess = Jess.start(message_handler, get_extensions())

def main():
    print("starting")
    application = Application.builder().bot(bot).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    get_chat_handler = CommandHandler('get_chat_id', get_chat_id)
    application.add_handler(get_chat_handler)
    drop_chat_handler = CommandHandler('drop_chat', drop_chat)
    application.add_handler(drop_chat_handler)

    echo_handler = MessageHandler(filters.TEXT, message)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
