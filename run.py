import time
import json

class Run(object):

    def __init__(self, run_id, thread_id, client, messages_handler, actions, logger):
        self.run_id = run_id
        self.thread_id = thread_id
        self.client = client
        self.messages_handler = messages_handler
        self.actions = actions
        self.logger = logger
        self._finished = False

    def run_status(self):
        status = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=self.run_id
        ).status
        self.logger.debug(f"run status: {status}")
        return status
    
    def cancel(self):
        self.client.beta.threads.runs.cancel(
            thread_id=self.thread_id,
            run_id=self.run_id
        )
        self._finished = True

    def finished(self):
        return self._finished
    
    def execute(self):
        run_status = ""
        while run_status not in ["completed", "failed", "canceled", "expired"]:
            run_status = self.run_status()
            if run_status == "in_progress":
                pass
            elif run_status == "cancelling":
                pass
            elif run_status == "requires_action":
                self._handle_actions()
            time.sleep(1)
        self.logger.debug("looks like we are done, checking if completed succesfully")
        if self.run_status() == "completed":
            self.logger.debug("success, now checking messages to send")
            self.messages_handler.on_messages(self._extract_messages())
        self._finished = True

    def _extract_messages(self):
        self.logger.debug("starting messages extraction")
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread_id
        )
        for message in messages:
            self.logger.debug(f"message_run_id: {message.run_id}, our run_id: {self.run_id}, value: {message.content[0].text.value}")
        return [message.content[0].text.value for message in messages if message.run_id == self.run_id]        

    def _handle_actions(self):
        self.logger.debug("strting handle action step")
        run_data = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=self.run_id
        )
        call_outputs = []
        for call_data in run_data.required_action.submit_tool_outputs.tool_calls:
            call_outputs.append(self._handle_action(call_data))
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=call_outputs
        )     
    
    def _handle_action(self, action):
        call_id = action.id
        funciton_name = action.function.name
        arg_string = action.function.arguments
        args = json.loads(arg_string)
        output = ""
        try:
            output = self.actions[funciton_name](**args)
        except Exception as e:
            output = f"call to {funciton_name} failed with {str(e)}" 
        return {
            "tool_call_id": call_id,
            "output": output
        }