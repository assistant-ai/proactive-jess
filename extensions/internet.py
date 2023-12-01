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
    final_result = []
    for url in result:
        try:
            article = _get_article(url)
            if article.text == "":
                continue
            if article.title == "Are you a robot?":
                continue
            final_result.append({
                "title": article.title,
                "url": url
            })
        except Exception as e:
            continue
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
    description="get raw HTML of a specific url provided. Should be used if site does not have an article but something else, in this case you can just get all HTML from the site and look on it",
    param_descriptions={
        "url": "url, from where to download the HTML"
    }
)
def get_raw_html(url: str):
    article = _get_article(url)
    return article.html


@jess_extension(
    description="get text of a specific url provided",
    param_descriptions={
        "url": "url, from where to extract text for you to read"
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