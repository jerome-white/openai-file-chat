import os
import json
from tempfile import NamedTemporaryFile

import gradio as gr
from openai import OpenAI

from mylib import (
    Logger,
    FileManager,
    ChatController,
    MessageHandler,
    NumericCitations,
)

#
#
#
class ErrorLogger:
    def __init__(self, path):
        self.path = path
        if not self.path.exists():
            self.path.mkdir(parents=True, exist_ok=True)

    def dump(self, prompt, error):
        msg = {
            'prompt': prompt,
        }
        msg.update(error.to_dict())
        output = json.dumps(msg, indent=2)

        with NamedTemporaryFile(mode='w',
                                prefix='',
                                dir=self.path,
                                delete=False) as fp:
            print(output, file=fp)
            return fp.name

#
#
#
class FileChat:
    def __init__(self, client, config):
        self.database = FileManager(client, config['chat']['prefix'])
        self.messenger = MessageHandler(client, NumericCitations)
        self.chat = ChatController(client, config['openai'], config['chat'])

    def upload(self, *args):
        (data, ) = args
        return self.database(data)

    def prompt(self, *args):
        (message, *_) = args
        if not self.database:
            raise gr.Error('Please upload your documents to begin')

        return self.messenger(self.chat(message, self.database))

#
#
#
with open(os.getenv('FILE_CHAT_CONFIG')) as fp:
    config = json.load(fp)

with gr.Blocks() as demo:
    client = OpenAI(api_key=config['openai']['api_key'])
    mychat = FileChat(client, config)

    with gr.Row():
        upload = gr.UploadButton(file_count='multiple')
        text = gr.Textbox(label='Files uploaded', interactive=False)
        upload.upload(mychat.upload, upload, text)

    gr.ChatInterface(
        fn=mychat.prompt,
        additional_inputs=[
            upload,
            text,
        ],
        retry_btn=None,
        undo_btn=None,
        clear_btn=None,
        # additional_inputs_accordion=gr.Accordion(
        #     label='Upload documents',
        #     open=True,
        # ),
    )

if __name__ == '__main__':
    # demo.queue().launch(server_name='0.0.0.0', **config['gradio'])
    demo.queue().launch(server_name='0.0.0.0')
