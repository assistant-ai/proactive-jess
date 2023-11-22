import threading
import time
import logging
import sys
import json
import time


from memory_extension import Memory
from openai import OpenAI
from run import Run
from jess_extension import jess_extension, get_openai_spec
from google_calendar_extension import get_upcoming_calendar_events


logging.basicConfig(level=logging.ERROR, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def read_jeff_instructions():
    with open("jess_prompt.txt") as f:
        return f.read()
    return ""


instructions = read_jeff_instructions()

memory = Memory.create_memory_extension()

extensions = {
    "store_in_long_term_memory": memory.store_in_long_term_memory,
    "query_from_long_term_memory": memory.query_from_long_term_memory,
    "get_upcoming_calendar_events": get_upcoming_calendar_events
}


class Jess(object):

    def __init__(self, client, assistent, message_handler) -> None:
        self.run = None
        self.thread = client.beta.threads.create(
            messages=[]
        )
        self.assistent = assistent
        self.stopped = False
        self.client = client
        self.next_action_time = None
        self.next_message = None
        self.message_handler = message_handler

    def stop(self):
        self.stopped = True

    def _cancel_scheduled_message(self):
        self.next_action_time = None
        self.next_message = None

    def send_message(self, message_to_send):
        self._cancel_scheduled_message()
        self._send_message(message_to_send)
        self._send_system_message_about_action()
        
    def _send_message(self, message_to_send):
        while self.run and not self.run.finished():
            time.sleep(1)
        
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message_to_send
        )
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistent.id
        )
        self.run = Run(run.id, self.thread.id, self.client, self, extensions, logger)  
        self.run.execute()      

    @jess_extension(
        description="Schedule next message to be sent to a user if there is no response from the user after a defined period of time.",
        param_descriptions={
            "sec_delay": "Amount of seconds from now when the message should be sent.",
            "message": "Message to be sent to the user."
        }
    )
    def schedule_message(self, sec_delay: int, message: str):
        self.next_action_time = time.time() + int(sec_delay)
        self.next_message = message
        return "DONE"

    def on_messages(self, messages):
        for message in messages:
            if message:
                self.message_handler(message)

    def _send_system_message_about_action(self):
        self._send_message("*SYSTEM* This is not real user message, and user will not read it. This message allows you to make schedule a pro-active message to a user, if user will not respond to you any time soon by using schedule_message action. Message that you might schedule will be canceled if the user will answer to you first. Do NOT reply to this message anything.")

    def execute(self):
        logger.debug("Starting Jess")
        while not self.stopped:
            logger.debug("Checking run status")
            if self.next_action_time and time.time() >= self.next_action_time:
                logger.debug("now")
                self.on_messages([self.next_message])
                self.next_action_time = None
                self.next_message = None
                self._send_system_message_about_action()
            time.sleep(2)

    @staticmethod
    def start(message_handler):
        JESS_NAME = "Jess"
        client = OpenAI()
        tools = [get_openai_spec(Jess.schedule_message)]
        for extension_name in extensions.keys():
            tools.append(get_openai_spec(extensions[extension_name]))
        jess_assitent_args = {
            "name": JESS_NAME,
            "instructions": instructions,
            "tools": tools,
            "model": "gpt-4-1106-preview"
        }
        jess_assitent = None
        for assistant in client.beta.assistants.list():
            if assistant.name == JESS_NAME:
                jess_assitent = assistant
                logger.debug("Found assistant")
                break

        if not jess_assitent:
            logger.debug("Creating new assistant")
            jess_assitent = client.beta.assistants.create(
                **jess_assitent_args
            )
        else:
            logger.debug("Updating assistant")
            jess_assitent = client.beta.assistants.update(
                assistant_id=jess_assitent.id,
                **jess_assitent_args
            )
        jess = Jess(client, jess_assitent, message_handler)
        extensions["schedule_message"] = jess.schedule_message
        thread = threading.Thread(target=jess.execute)
        thread.start()
        return jess

def message_handler(message):
    print("jess: " + message + "\n")

if __name__ == "__main__":
    jess = Jess.start(message_handler)
    # while loop with the read from keyboard and send message
    while True:
        message_to_send = input("You: ")
        jess.send_message(message_to_send)
        time.sleep(3)