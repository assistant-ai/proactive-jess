import datetime
import json

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


@jess_extension(
    description="Query Google and get back 10 urls from Google for the query",
    param_descriptions={
        "query": "Query to search for"
    }
)
def google(query: str):
    result = json.dumps([url for url in search(query, num_results=10)])
    print(result)
    return result


@jess_extension(
    description="read article from the url provided (can be used together with the google query)",
    param_descriptions={
        "url": "url to read"
    }
)
def get_text_from_url(url: str):
    article = Article(url)
    print("article object created")
    article.download()
    if article.download_state != ArticleDownloadState.SUCCESS:
       article.html = urllib.request.urlopen(url).read()
       # Hacking the library
       article.download_state = ArticleDownloadState.SUCCESS
    print("download completed")
    article.parse()
    print("parsing completed")

    return json.dumps(
        {
            "title": article.title,
            "text": article.text
        }
    )


if __name__ == "__main__":
    print(google("test"))