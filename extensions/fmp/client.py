import os
import json
from urllib.request import urlopen
import certifi
from dotenv import load_dotenv
from datetime import datetime, timedelta
from extensions.jess_extension import jess_extension
from rest.token_management import get_user_id
from db import get_user_data
from rest.main_app import app
from quart import jsonify, request


class FMP(object):

    def __init__(self, key, as_string=True):
        self.key = key
        self.as_string = as_string

    def _get_jsonparsed_data(self, url):
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)

    def get_economic_calendar(self, from_date, to_date, filter_low=True):
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={from_date}&to={to_date}&apikey={self.key}"
        events = self._get_jsonparsed_data(url)
        if filter_low:
            events = [event for event in events if event.get('impact') != "Low" and event.get('country') == "US"]
        if self.as_string:
            return json.dumps(events)
        return events
    
    @jess_extension(
    description="Get all the latest important news that have happened recently (and can impact markets).",
        param_descriptions={}
    )
    def get_financial_news(self):
        url = f"https://financialmodelingprep.com/api/v3/stock_news?page=0&apikey={self.key}"
        news = self._get_jsonparsed_data(url)
        if self.as_string:
            return json.dumps(news)
        return news
    
    @jess_extension(
    description="Get all the latest important news related to a specific ticker.",
        param_descriptions={
            "ticker": "Ticker symbol of the stock, for which news needs to be retrived."
        }
    )
    def get_financial_news_about_specific_ticker(self, ticker: str):
        url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&limit=10&page=0&apikey={self.key}"
        news = self._get_jsonparsed_data(url)
        # Filter for the latest 20 articles and extract only title and URL
        filtered_news = [{"title": article["title"], "url": article["url"]} for article in news[:20]]

        if self.as_string:
            return json.dumps(filtered_news)
        return filtered_news
    
    @jess_extension(
    description="Get all the important ecenomica events for the next 7 days that might impact market.",
        param_descriptions={}
    )
    def get_events_next_week(self):
        today = datetime.now().date()  # Get the current date without time
        next_week_start = today + timedelta(days=(7 - today.weekday()))
        next_week_end = next_week_start + timedelta(days=6)
        return self.get_economic_calendar(next_week_start, next_week_end)

    @jess_extension(
    description="Get all the important ecenomica events for the next day that might impact market.",
        param_descriptions={}
    )
    def get_events_next_day(self):
        today = datetime.now().date()  # Get the current date without time
        next_day = today + timedelta(days=1)
        return self.get_economic_calendar(next_day, next_day)

    @staticmethod
    def create_fmp():
        load_dotenv()
        key = os.getenv('FMP_KEY')
        return FMP(key)
    
    @staticmethod
    def create_fmp_from_request():
        token = request.headers.get('Authorization').split(' ')[1]
        if not token:
            raise Exception("please re-authentificate")
        user_id = None
        try:
            user_id = get_user_id(token)
        except:
            raise Exception("please re-authentificate")
        if not user_id:
            raise Exception("please re-authentificate")
        user_data = get_user_data(user_id)
        key = user_data['FMP_KEY']
        return FMP(key)
    


@app.route('/financial/fmp/news', methods=['GET'])
async def financial_news():
    fmp = FMP.create_fmp_from_request()
    return jsonify(fmp.get_financial_news()), 200

@app.route('/financial/fmp/news/ticker', methods=['GET'])
def financial_news_ticker():
    fmp = FMP.create_fmp_from_request()
    ticker = request.args.get('ticker')
    if not ticker:
        return jsonify({"error": "Ticker parameter is missing"}), 400
    return jsonify(fmp.get_financial_news_about_specific_ticker(ticker)), 200

@app.route('/financial/fmp/events/nextweek', methods=['GET'])
def events_next_week():
    fmp = FMP.create_fmp_from_request()
    return jsonify(fmp.get_events_next_week()), 200

@app.route('/financial/fmp/events/nextday', methods=['GET'])
def events_next_day():
    fmp = FMP.create_fmp_from_request()
    return jsonify(fmp.get_events_next_day()), 200

    
if __name__ == "__main__":
    fmp = FMP.create_fmp()
    print(fmp.get_financial_news())