import time
import json

class Run(object):

    def __init__(self, run_id, thread_id, client, messages_handler, actions):
        self.run_id = run_id
        self.thread_id = thread_id
        self.client = client
        self.messages_handler = messages_handler
        self.actions = actions

    def run_status(self):
        return self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=self.run_id
        ).status
    
    def cancel(self):
        self.client.beta.threads.runs.cancel(
            thread_id=self.thread_id,
            run_id=self.run_id
        )

    def finished(self):
        run_status = self.run_status()
        return run_status in ["completed", "failed", "canceled", "expired"]
    
    def execute(self):
        while not self.finished():
            if self.run_status() == "in_progress":
                pass
            elif self.run_status() == "cancelling":
                pass
            elif self.run_status() == "requires_action":
                self._handle_actions()
            time.sleep(1)
        if self.run_status() == "completed":
            self.messages_handler.on_messages(self._extract_messages())

    def _extract_messages(self):
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread_id
        )
        return [message.content[0].text.value for message in messages if message.run_id == self.run_id]        

    def _handle_actions(self):
        run_data = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id,
            run_id=self.run_id
        )
        for call_data in run_data.required_action.submit_tool_outputs.tool_calls:
            self._handle_action(call_data)        
    
    def _handle_action(self, action):
        call_id = action.id
        funciton_name = action.function.name
        arg_string = action.function.arguments
        args = json.loads(arg_string)
        output = self.actions[funciton_name](**args)
        self.client.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread_id,
            run_id=self.run_id,
            tool_outputs=[
                {
                    "tool_call_id": call_id,
                    "output": output
                }
            ]
        )