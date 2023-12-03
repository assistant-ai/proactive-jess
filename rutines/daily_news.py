class DailyNewsRutine(object):

    def __init__(self, jess, schedule) -> None:
        self.jess = jess
        schedule.every().day.at("05:50", "America/Los_Angeles").do(self.do_daily_news)

    def do_daily_news(self):
        self.jess.send_message("What are the latest financial news. Use your extensions to check and give me TLDR, pick top(by your own feeling of importance) 10 only.")
