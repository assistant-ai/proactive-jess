
import threading
import time
import logging
import sys
import json

from openai import OpenAI


logging.basicConfig(level=logging.ERROR, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def read_jeff_instructions():
    with open("jess_prompt.txt") as f:
        return f.read()
    return ""


instructions = read_jeff_instructions()


function_to_schedule_message = {
    "type": "function",
    "function": {
        "name": "schedule_message",
        "description": "Schedule next message to be sent to a user if there is not response from user after a defined period of time.",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "integer", 
                    "description": "Amount of second from now when the message should be sent."
                },
                "message": {
                    "type": "string", 
                    "description": "Message to be sent to the user."
                },
            },
            "required": ["message", "time"]
        }
    }
} 


class Jess(object):

    def __init__(self, client, assistent) -> None:
        self.run = None
        self.thread = client.beta.threads.create(
            messages=[]
        )
        # create lock variable for the thread
        self.lock = threading.Lock()
        self.assistent = assistent
        self.stopped = False
        self.client = client
        self.next_action_time = None
        self.last_status = None

    def stop(self):
        self.stopped = True

    def cancel_current_run(self):
        self.lock.acquire()
        if not self.run:
            self.lock.release()
            return
        run_status = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        if run_status.status != "requires_action":
            self.lock.release()
            return
        self.client.beta.threads.runs.cancel(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        self.run = None
        self.lock.release()
        
    def send_message(self, message_to_send):
        self.cancel_current_run()
        self.lock.acquire()
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message_to_send
        )
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistent.id
        )
        self.lock.release()

    def _send_system_message_about_action(self):
        logger.debug("Sending system message about action")
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="*SYSTEM* This is not real user message, and user will not read it. This message allows you to make schedule a pro-active message to a user, if user will not respond to you any time soon by using schedule_message action. Message that you might schedule will be canceled if the user will answer to you first."
        )
        self.run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistent.id
        )

    def _print_jess_message(self, message):
        print("Jess: " + message + "\nYou: ")

    def _check_need_to_send_proactive_message(self):
        if not self.next_action_time:
            return False
        logger.debug(f"checking time next_action_time: {self.next_action_time}, current time: {time.time()}, message: {self.next_message}")
        if time.time() >= self.next_action_time:
            return True
        return False
    
    def _is_current_run_completed(self):
        if not self.run:
            return False
        run_status = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.run.id
        )
        logger.debug(f"run_status: {run_status.status}")
        return run_status.status == "completed"

    def execute(self):
        logger.debug("Starting Jess")
        while not self.stopped:
            logger.debug("Checking run status")
            self.lock.acquire()
            # check if run is completed and if last status was None or required aciton
            #    print messages
            #    check if proactive message need to be initiated
            # check if run is requires_action
            #    execute action
            self.lock.release()
            return
            if not self.run:
                if self.last_status and self.last_status == "requires_action":
                    self.last_status = None
                    self._send_system_message_about_action()
                self.lock.release()
                time.sleep(1)
                continue
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=self.run.id
            )
            logger.debug(f"run_status: {run_status.status}")
            if run_status.status == "completed":
                if self.last_status and self.last_status == "requires_action":
                    self.last_status = None
                else:
                    messages = self.client.beta.threads.messages.list(
                        thread_id=self.thread.id
                    )
                    self._print_jess_message(list(messages)[0].content[0].text.value)
                self._send_system_message_about_action()
            if run_status.status == "requires_action":
                if self.next_action_time:
                    logger.debug(f"checking time next_action_time: {self.next_action_time}, current time: {time.time()}, message: {self.next_message}")
                    if time.time() >= self.next_action_time:
                        logger.debug("now")
                        call_data = run_status.required_action.submit_tool_outputs.tool_calls[0]
                        call_id = call_data.id
                        arg_string = call_data.function.arguments
                        args = json.loads(arg_string)
                        arugment_message = args["message"]
                        self.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=self.thread.id,
                            run_id=self.run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call_id,
                                    "output": "done"
                                }
                            ]
                        )
                        self.next_action_time = None
                        self._print_jess_message(arugment_message)
                        self.last_status = "requires_action"
                    else:
                        logger.debug("not yet")
                else:
                    call_data = run_status.required_action.submit_tool_outputs.tool_calls[0]
                    arg_string = call_data.function.arguments
                    args = json.loads(arg_string)
                    arugment_time = args["time"]
                    arugment_message = args["message"]
                    # arugment_time is in seconds from now
                    self.next_action_time = time.time() + int(arugment_time)
                    self.next_message = arugment_message
                    logger.debug(f"next_action_time: {self.next_action_time}, text: {arugment_message}, current time: {time.time()}")
            self.lock.release()
            time.sleep(1)

    @staticmethod
    def start():
        JESS_NAME = "Jess"
        client = OpenAI()
        jess_assitent_args = {
            "name": JESS_NAME,
            "instructions": instructions,
            "tools": [function_to_schedule_message],
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
        jess = Jess(client, jess_assitent)
        thread = threading.Thread(target=jess.execute)
        thread.start()
        return jess

if __name__ == "__main__":
    jess = Jess.start()
    # while loop with the read from keyboard and send message
    while True:
        message_to_send = input("You: ")
        jess.send_message(message_to_send)
        time.sleep(3)
    # jess.send_message("Hello")
    # time.sleep(10)
    # jess.stop()
    # time.sleep(2)
    # print("done")