from urllib.parse import quote
import os
import requests
from dotenv import load_dotenv

load_dotenv()


telegram_token = os.getenv('TELEGRAM_TOKEN')

def send_message(chat_id, message_to_send):
    print(message_to_send)
    encoded_message = quote(message_to_send)
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={encoded_message}"
    result = requests.get(url).json()
    print("answer is: " + str(result))
    return result