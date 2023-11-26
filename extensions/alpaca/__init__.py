import alpaca_trade_api as tradeapi
import os

from dotenv import load_dotenv

load_dotenv()

api =  None

def get_api(test_api=True):
    global api
    if api:
        return api
    api_key = os.getenv('ALPACA_KEY_NAME')
    api_secret = os.getenv('ALPACA_KEY_SECRET')
    base_url = 'https://paper-api.alpaca.markets'  
    if not test_api:
        base_url = "https://api.alpaca.markets"
    api = tradeapi.REST(key_id=api_key, secret_key=api_secret, base_url=base_url, api_version='v2')
    return api
