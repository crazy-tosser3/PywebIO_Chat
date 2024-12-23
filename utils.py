import json
import os
import asyncio
from config import MSG_FILE , chat_msgs , MAX_MSG_COUNT , USERS_BASE
from pywebio import start_server
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *

def load_user():
    global Users
    with open(USERS_BASE, 'r', encoding='utf-8') as f:
        Users = json.load(f)
        return Users


def load_messages():
    global chat_msgs
    if os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'r', encoding='utf-8') as f:
            chat_msgs = json.load(f)

def save_messages():
    global chat_msgs
    with open(MSG_FILE, 'w', encoding='utf-8') as f:
        json.dump(chat_msgs, f)

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)
        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        if len(chat_msgs) > MAX_MSG_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)
