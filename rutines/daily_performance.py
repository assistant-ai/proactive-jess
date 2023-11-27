class DailyPerformanceRutine(object):

    def __init__(self, jess, schedule) -> None:
        self.jess = jess
        schedule.every().day.at("09:00").do(self.do_performance_overview)

    def do_performance_overview(self):
        self.jess.send_message("can you show me my investment performance")
