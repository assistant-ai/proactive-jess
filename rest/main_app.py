import quart_cors
import os
from dotenv import load_dotenv

from quart import Quart

load_dotenv()


secret_key = os.getenv('REST_API_SECRET_KEY')

app = quart_cors.cors(Quart(__name__), allow_origin=["http://localhost:5555", "https://chat.openai.com"])
app.secret_key = secret_key

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'