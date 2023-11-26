import os
import json
from urllib.request import urlopen
import certifi
from dotenv import load_dotenv
from datetime import datetime, timedelta
from extensions.jess_extension import jess_extension


class FMP(object):

    def __init__(self, key):
        self.key = key

    def _get_jsonparsed_data(self, url):
        response = urlopen(url, cafile=certifi.where())
        data = response.read().decode("utf-8")
        return json.loads(data)

    def get_economic_calendar(self, from_date, to_date, filter_low=True):
        url = f"https://financialmodelingprep.com/api/v3/economic_calendar?from={from_date}&to={to_date}&apikey={self.key}"
        events = self._get_jsonparsed_data(url)
        if filter_low:
            events = [event for event in events if event.get('impact') != "Low" and event.get('country') == "US"]
        return json.dumps(events)
    
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
    
if __name__ == "__main__":
    fmp = FMP.create_fmp()
    print(fmp.get_events_next_day())