from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()

async def start(update, context):
    await update.message.reply_text('Hello! I am your bot.')

async def echo(update, context):
    await update.message.reply_text(update.message.text)


def main():
    token = os.getenv('TELEGRAM_TOKEN') 
    application = Application.builder().token(token).build()
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    echo_handler = MessageHandler(filters.TEXT, echo)
    application.add_handler(echo_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
