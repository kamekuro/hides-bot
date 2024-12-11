#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import re
import json
import typing
import logging
import traceback

import pyrogram
from pyrogram import filters, types, enums

import utils
from loader import cache


def StateFilter(state: str):
    async def func(flt, client: pyrogram.Client, update: types.Update):
        conv = await cache.get(str(update.from_user.id), {})
        if conv.get("name") != state:
            return False
        if conv.get("bot_id") != client.me.id:
            return False

        if isinstance(update, types.Message):
            if conv.get("chat_id") != update.chat.id:
                return False
        elif isinstance(update, types.CallbackQuery):
            if conv.get("chat_id") != update.message.chat.id:
                return False

        await cache.delete(str(update.from_user.id))
        return True

    return filters.create(
        func,
        "StateFilter",
        state=state
    )


async def set_state(client: pyrogram.Client, name: str, user_id: int, chat_id: int = 0):
    conv = await cache.get(str(user_id), {})
    conv['name'] = name
    conv['bot_id'] = client.me.id
    conv['chat_id'] = chat_id if chat_id != 0 else None
    await cache.set(str(user_id), conv)