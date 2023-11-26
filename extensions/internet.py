import json
import urllib

from newspaper import Article
from newspaper.article import ArticleDownloadState

from .jess_extension import jess_extension
from googlesearch import search

urls = {}

@jess_extension(
    description="Query Google and get back 10 urls from Google for the query",
    param_descriptions={
        "query": "Query to search for"
    }
)
def google(query: str):
    result = [url for url in search(query, num_results=10)]
    final_result = [{
        "title": _get_article(url).title,
        "url": url
    } for url in result]
    print(str(final_result))
    return json.dumps(final_result)

def _get_article(url):
    if url in urls:
        return urls[url]
    article = Article(url)
    article.download()
    if article.download_state != ArticleDownloadState.SUCCESS:
       article.html = urllib.request.urlopen(url).read()
       # Hacking the library
       article.download_state = ArticleDownloadState.SUCCESS
    article.parse()
    urls[url] = article
    return article


@jess_extension(
    description="read article from the url provided (can be used together with the google query)",
    param_descriptions={
        "url": "url to read"
    }
)
def get_text_from_url(url: str):
    article = _get_article(url)

    return json.dumps(
        {
            "title": article.title,
            "text": article.text
        }
    )