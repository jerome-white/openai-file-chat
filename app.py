import os
import json
import functools as ft
import collections as cl
from pathlib import Path

import gradio as gr
from openai import OpenAI

from mylib import (
    FileManager,
    ChatController,
    MessageHandler,
    NumericCitations,
)

#
#
#
ChatState = cl.namedtuple('ChatState', 'database, messenger, chat')

@ft.cache
def scancfg():
    with open(os.getenv('FILE_CHAT_CONFIG')) as fp:
        return json.load(fp)

#
#
#
def load():
    config = scancfg()
    (_openai, _chat) = map(config.get, ('openai', 'chat'))
    client = OpenAI(api_key=_openai['api_key'])

    database = FileManager(client, _chat['prefix'])
    messenger = MessageHandler(client, NumericCitations)
    chat = ChatController(client, database, _openai, _chat)

    return ChatState(database, messenger, chat)

def eject(state):
    state.database.cleanup()
    state.chat.cleanup()

def upload(data, state):
    return state.database(data)

def prompt(message, history, state):
    if state.database:
        response = state.messenger(state.chat(message))
        history.append((
            message,
            response,
        ))
    else:
        gr.Warning('Please upload your documents to begin')

    return (     # textbox submit outputs
        '',      # clear the input text
        history, # update the chat output
    )

#
#
#
with gr.Blocks() as demo:
    state = gr.State(
        value=load,
        delete_callback=eject,
    )
    howto = Path('static/howto').with_suffix('.md')

    with gr.Row():
        with gr.Accordion(label='Instructions', open=False):
            gr.Markdown(howto.read_text())
    with gr.Row():

        with gr.Column():
            data = gr.UploadButton(
                label='Select and upload your files',
                file_count='multiple',
            )
            repository = gr.Textbox(
                label='Files uploaded',
                placeholder='Upload your files to begin!',
                interactive=False,
            )
            data.upload(
                fn=upload,
                inputs=[
                    data,
                    state,
                ],
                outputs=repository,
            )

        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                height='70vh',
                scroll_to_output=True,
                show_copy_button=True,
            )
            interaction = gr.Textbox(
                label='Ask a question about your documents and press "Enter"',
            )
            interaction.submit(
                fn=prompt,
                inputs=[
                    interaction,
                    chatbot,
                    state,
                ],
                outputs=[
                    interaction,
                    chatbot,
                ],
            )

if __name__ == '__main__':
    kwargs = scancfg().get('gradio')
    demo.queue().launch(server_name='0.0.0.0', **kwargs)
