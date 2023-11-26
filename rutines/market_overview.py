from prompts import investing_forecast_prompt as prompt


class MarketOverviewRutine(object):

    def __init__(self, jess, schedule) -> None:
        self.jess = jess
        schedule.every().sunday.at("20:00").do(self.send_market_overview)

    def send_market_overview(self):
        self.jess.send_message(prompt)
