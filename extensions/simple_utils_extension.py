import datetime
import json
import urllib

from newspaper import Article
from newspaper.article import ArticleDownloadState

from .jess_extension import jess_extension
from rest.main_app import app
from quart import jsonify


@jess_extension(
    description="Get current date/time",
    param_descriptions={}
)
def current_date_time():
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time in a readable format
    return now.strftime("%Y-%m-%d %H:%M:%S")


@app.route('/current/datetime', methods=['GET'])
async def get_current_date_time():
    return jsonify({
        "datetime": current_date_time()
    }), 200