from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Bot
from dotenv import load_dotenv
from jess import Jess
import os
import asyncio

load_dotenv()

async def start(update, context):
    await update.message.reply_text('Hello! I am your bot.')

async def message(update, context):
    jess.send_message(update.message.text)

async def get_chat_id(update, context):
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Your chat ID is: {chat_id}")

def message_handler(meesage):
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
    # Define the coroutine
    coroutine = bot.send_message(chat_id=chat_id, text=message)

    # Get the current event loop
    loop = asyncio.get_event_loop()

    # Schedule the coroutine to be run on the event loop
    future = asyncio.run_coroutine_threadsafe(coroutine, loop)

    # Optionally, wait for the future to complete (if you need to know the result or catch exceptions)
    result = future.result()
    # asyncio.get_event_loop().run_until_complete(bot.send_message(chat_id=chat_id, text=meesage))
    # await bot.send_message(chat_id=chat_id, text=meesage)

jess = Jess.start(message_handler)
# # while loop with the read from keyboard and send message
# while True:
#     message_to_send = input("You: ")
#     jess.send_message(message_to_send)
#     time.sleep(3)

def main():
    token = os.getenv('TELEGRAM_TOKEN') 
    application = Application.builder().token(token).build()
    start_handler = CommandHandler('start', start)
    start_handler = CommandHandler('get_chat_id', get_chat_id)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT, message)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
