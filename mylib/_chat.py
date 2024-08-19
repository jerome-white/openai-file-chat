import math
import time
from pathlib import Path

import pandas as pd

from ._logging import Logger

def parse_wait_time(err):
    if err.code == 'rate_limit_exceeded':
        for i in err.message.split('. '):
            if i.startswith('Please try again in'):
                (*_, wait) = i.split()
                return (pd
                        .to_timedelta(wait)
                        .total_seconds())

    raise TypeError(err.code)

class ChatController:
    _gpt_defaults = {
        'model': 'gpt-4o',
        'max_completion_tokens': 2 ** 12,
    }

    def __init__(self, client, gpt, chat):
        self.client = client
        self.gpt = gpt
        self.chat = chat

        for i in self._gpt_defaults.items():
            self.gpt.setdefault(*i)
        instructions = Path(self.chat['system_prompt'])

        self.assistant = self.client.beta.assistants.create(
            name=self.gpt['assistant_name'],
            model=self.gpt['model'],
            instructions=instructions.read_text(),
            temperature=0.1,
            tools=[{
                'type': 'file_search',
            }],
        )
        self.thread = self.client.beta.threads.create()
        self.attached = False

    def __call__(self, prompt, database):
        if not self.attached:
            self.client.beta.assistants.update(
                assistant_id=self.assistant.id,
                tool_resources={
                    'file_search': {
                        'vector_store_ids': [
                            database.vector_store_id,
                        ],
                    },
                },
            )
            self.attached = True

        return self.send(prompt)

    def send(self, content):
        self.client.beta.threads.messages.create(
            self.thread.id,
            role='user',
            content=content,
        )

        for i in range(self.chat['retries']):
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id,
            )
            if run.status == 'completed':
                return self.client.beta.threads.messages.list(
                    thread_id=self.thread.id,
                    run_id=run.id,
                )
            Logger.error('%s (%d): %s', run.status, i + 1, run.last_error)

            rest = math.ceil(parse_wait_time(run.last_error))
            Logger.warning('Sleeping %ds', rest)
            time.sleep(rest)

        raise TimeoutError('Message retries exceeded')
