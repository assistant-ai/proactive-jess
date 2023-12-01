import schedule
import time
import threading
from .market_overview import MarketOverviewRutine
from .daily_performance import DailyPerformanceRutine
from .drop_chat_thread_context import DropChatThreadRutine
from .daily_news import DailyNewsRutine


class RutineScheduler():

    def __init__(self, jess, schedule):
        self.jess = jess
        self.schedule = schedule

    @staticmethod
    def start_rutines(jess, schedule=schedule):
        MarketOverviewRutine(jess, schedule)
        DailyPerformanceRutine(jess, schedule)
        DropChatThreadRutine(jess, schedule)
        DailyNewsRutine(jess, schedule)
        rutine_scheduler = RutineScheduler(jess, schedule)
        thread = threading.Thread(target=rutine_scheduler._run)
        thread.start()
        return rutine_scheduler

    def _run(self):
        while True:
            self.schedule.run_pending()
            time.sleep(5)
