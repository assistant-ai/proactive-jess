from prompts import investing_forecast_prompt as prompt


class DropChatThreadRutine(object):

    def __init__(self, jess, schedule) -> None:
        self.jess = jess
        schedule.every().day.at("01:00", "America/Los_Angeles").do(self.drop_chat_thread)

    def drop_chat_thread(self):
        self.jess.drop_chat_thread()
