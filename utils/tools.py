#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import attrify
import base64
import functools
import logging
import io
import json
import re
import struct
import time
import typing

import pyrogram
from pyrogram import types

from db import DataBase

config = json.loads(open("config.json", "r", encoding="utf-8").read())
db = DataBase()

init_ts = time.perf_counter()


def init_db():
    db.save("""CREATE TABLE IF NOT EXISTS users( 
        id INT PRIMARY KEY,
        status INT DEFAULT 0,
        lang TEXT DEFAULT "ru"
    )""")
    db.regUser(config['dev_id'], status=2)


def printMe():
    print(f"\033[36m          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █\033[0m")
    print(f"\033[36m          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄\033[0m")
    print(f"\033[36m                © Copyright 2024\033[0m", end="\n\n")
    print(f"\033[36m            👤 https://t.me/unneyon\033[0m", end="\n\n")
    print(f"\033[36m 🔒 Licensed under the GNU GPLv3\033[0m")
    print(f"\033[36m 🌐 https://www.gnu.org/licenses/agpl-3.0.html\033[0m", end="\n\n")


def checkConfig():
    all_items = ["token", "id", "dev_id", "commands", "app"]
    items = []
    for i in all_items:
        if not config.get(i):
            items.append(i)
    if len(items) != 0:
        error = f"\033[31mВ файле \033[36mconfig.json\033[31m отсутству{'e' if len(items) == 1 else 'ю'}т " \
                f"пол{'e' if len(items) == 1 else 'я'} \033[36m{', '.join(items)}\033[31m!\033[0m"
        exit(error)


async def sendBackup():
    from loader import client

    dbf = io.BytesIO(open("db.db", "rb").read())
    dbf.name = "db.db"
    dbf = pyrogram.types.InputMediaDocument(dbf)
    cfgf = io.BytesIO(open("config.json", "rb").read())
    cfgf.name = "config.json"
    cfgf = pyrogram.types.InputMediaDocument(cfgf, caption="#backup")

    await client.send_media_group(
        chat_id=config['admin_chat'] if config['admin_chat'] != 0 else config['dev_id'],
        media=[dbf, cfgf],
        disable_notification=True
    )


def censor(ret: str) -> str:
    ret = ret.replace(config['token'], f'{config["token"].split(":")[0]}:{"*"*26}').replace(str(config['app']['id']), "*"*len(str(config['app']['id']))).replace(config['app']['hash'], "*"*len(config['app']['hash']))

    return ret


async def resolve_inine_message_id(client, inline_message_id):
    attrs = {
        "dc_id": None,
        "message_id": None,
        "chat_id": None,
        "query_id": None,
        "inline_message_id": None
    }
    dc_id, message_id, pid, query_id = struct.unpack(
        '<iiiq',
        base64.urlsafe_b64decode(
            inline_message_id + '=' * (len(inline_message_id) % 4)
        )
    )

    attrs['dc_id'] = dc_id
    attrs['message_id'] = message_id
    attrs['chat_id'] = int(str(pid))
    if not str(attrs['chat_id']).startswith("-100"):
        attrs['chat_id'] = int(f"-100{abs(attrs['chat_id'])}")
    attrs['query_id'] = query_id
    attrs['inline_message_id'] = inline_message_id

    return attrify.Attrify(attrs)

    
async def resolveByUsername(client, username):
    try:
        r = await client.invoke(
            pyrogram.raw.functions.contacts.ResolveUsername(username=username)
        )
    except:
        r = None
    try:
        c = await client.get_users(username)
    except:
        c = None

    if r and r.users:
        for i in r.users:
            if i.username == username:
                return i.id
    elif c:
        return c.id
    return 0

async def getIdByText(client, text):
    url = re.findall(r't\.me/([a-zA-Z0-9_\.]+)', text)
    if len(url) > 0:
        return await resolveByUsername(client, url[0])
    tag = re.findall(r'@([a-zA-Z0-9_\.]+)', text)
    if len(tag) > 0:
        return await resolveByUsername(client, tag[0])

    domain = await resolveByUsername(client, text)
    return domain

async def getID(message):
    if message.reply_to_message:
        if message.reply_to_message.forward_from:
            return message.reply_to_message.forward_from.id
        return message.reply_to_message.from_user.id

    args = get_args(message)
    text = ""
    if len(args) != 0:
        text = args[0]
    if str(text).isdigit():
        return int(text)

    return await getIdByText(message._client, text)


def pluralForm(count, variants):
    count = abs(count)
    if count % 10 == 1 and count % 100 != 11:
        var = 0
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        var = 1
    else:
        var = 2
    return f"{count} {variants[var]}"


async def resolve_inine_message_id(client, inline_message_id):
    attrs = {
        "dc_id": None,
        "message_id": None,
        "chat_id": None,
        "query_id": None,
        "inline_message_id": None
    }
    dc_id, message_id, pid, query_id = struct.unpack(
        '<iiiq',
        base64.urlsafe_b64decode(
            inline_message_id + '=' * (len(inline_message_id) % 4)
        )
    )

    attrs['dc_id'] = dc_id
    attrs['message_id'] = message_id
    attrs['chat_id'] = int(str(pid))
    if not str(attrs['chat_id']).startswith("-100"):
        attrs['chat_id'] = int(f"-100{abs(attrs['chat_id'])}")
    attrs['query_id'] = query_id
    attrs['inline_message_id'] = inline_message_id

    return attrify.Attrify(attrs)


def get_args(message):
    text = message.text or message.caption
    text = text.split(maxsplit=1)[1:]
    if len(text) == 0:
        return []
    return text[0].split()


def get_raw_args(message):
    text = message.text or message.caption
    text = text.split(maxsplit=1)[1:]
    if len(text) == 0:
        return ""
    return text[0]


def remove_html(text: str, keep_emojis: bool = False) -> str:
    return str(
        re.sub(
            (
                r"(<\/?a.*?>|<\/?b>|<\/?i>|<\/?u>|<\/?strong>|<\/?em>|<\/?code>|<\/?strike>|<\/?del>|<\/?pre.*?>)"
                if keep_emojis
                else r"(<\/?a.*?>|<\/?b>|<\/?i>|<\/?u>|<\/?strong>|<\/?em>|<\/?code>|<\/?strike>|<\/?del>|<\/?pre.*?>|<\/?emoji.*?>)"
            ),
            "",
            text,
        )
    )


def run_sync(func, *args, **kwargs):
    return asyncio.get_event_loop().run_in_executor(
        None,
        functools.partial(func, *args, **kwargs),
    )

def run_async(loop: asyncio.AbstractEventLoop, coro: typing.Awaitable) -> typing.Any:
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


async def answer(
    message: typing.Union[pyrogram.types.Message, pyrogram.Client],
    response: str = "",
    reply: bool = True,
    chat_id: int = 0,
    photo: typing.Union[str, typing.BinaryIO] = None,
    video: typing.Union[str, typing.BinaryIO] = None,
    sticker: typing.Union[str, typing.BinaryIO] = None,
    animation: typing.Union[str, typing.BinaryIO] = None,
    document: typing.Union[str, typing.BinaryIO] = None,
    media_group: typing.List[typing.Union[
        "pyrogram.types.InputMediaPhoto",
        "pyrogram.types.InputMediaVideo",
        "pyrogram.types.InputMediaAudio",
        "pyrogram.types.InputMediaDocument"
    ]] = None,
    **kwargs
) -> typing.Union[pyrogram.types.Message, typing.List]:
    if isinstance(message, list) and message:
        message = message[0]
        client = message._client
    elif isinstance(message, pyrogram.Client):
        client = message
        reply=False
    elif isinstance(message, pyrogram.types.Update):
        client = message._client
    response = censor(response)
    responses, msgs = [], []

    if len(response) > (1024 if (photo or animation or document) else 4096):
        for x in range(0, len(response), 1024 if (photo or animation or document) else 4096):
            responses.append(response[x:x+(1024 if (photo or animation or document) else 4096)])
    else:
        responses = [response]

    if photo:
        msgs.append(await client.send_photo(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            photo=photo,
            caption=responses[0],
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_to_message_id=message.id if reply else None,
                    disable_notification=True,
                    **kwargs
                ))
    elif video:
        msgs.append(await client.send_video(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            video=video,
            caption=responses[0],
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_to_message_id=message.id if reply else None,
                    disable_notification=True,
                    **kwargs
                ))
    elif sticker:
        msgs.append(await client.send_sticker(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            sticker=sticker,
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
    elif animation:
        msgs.append(await client.send_animation(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            animation=animation,
            caption=responses[0],
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_to_message_id=message.id if reply else None,
                    disable_notification=True,
                    **kwargs
                ))
    elif document:
        msgs.append(await client.send_document(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            document=document,
            caption=responses[0],
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_to_message_id=message.id if reply else None,
                    disable_notification=True,
                    **kwargs
                ))
    elif media_group:
        msgs.append(await client.send_media_group(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            media=media_group,
            reply_to_message_id=message.id if reply else None,
            disable_notification=True,
            **kwargs
        ))
        if len(responses) > 1:
            for resp in responses[1:]:
                msgs.append(await client.send_message(
                    chat_id=message.chat.id if chat_id == 0 else chat_id,
                    text=resp,
                    reply_to_message_id=message.id if reply else None,
                    disable_notification=True,
                    **kwargs
                ))
    else:
        for resp in responses:
            msgs.append(await client.send_message(
                chat_id=message.chat.id if chat_id == 0 else chat_id,
                text=resp,
                reply_to_message_id=message.id if reply else None,
                disable_notification=True,
                **kwargs
            ))
        
    return msgs if len(msgs) > 1 else msgs[0]


async def edit(
    message: pyrogram.types.Message,
    response: str = "",
    id: int = 0,
    chat_id: int = 0,
    media: typing.Union[
        "pyrogram.types.InputMediaPhoto",
        "pyrogram.types.InputMediaVideo",
        "pyrogram.types.InputMediaAudio",
        "pyrogram.types.InputMediaDocument"
    ] = None,
    **kwargs
) -> pyrogram.types.Message:
    if isinstance(message, list) and message:
        message = message[0]
    response = censor(response)

    if media:
        return await message._client.edit_message_media(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            message_id=message.id if id == 0 else id,
            media=media,
            **kwargs
        )
    else:
        return await message._client.edit_message_text(
            chat_id=message.chat.id if chat_id == 0 else chat_id,
            message_id=message.id if id == 0 else id,
            text=response,
            **kwargs
        )