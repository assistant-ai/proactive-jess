import datetime
import json
import urllib

from newspaper import Article
from newspaper.article import ArticleDownloadState

from .jess_extension import jess_extension
from googlesearch import search


@jess_extension(
    description="Get current date/time",
    param_descriptions={}
)
def current_date_time():
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time in a readable format
    return now.strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print(google("test"))