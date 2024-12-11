#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import datetime
import logging
import io
import random
import time

import pyrogram
import pyroboard
import pyrogram_patch
from pyrogram import types
from pyrogram_patch.router import Router

import utils
from dispatch import filters
from dispatch.fsm import StateFilter, set_state


other = Router()
other.name = "other"
logger = logging.getLogger(__name__)


@other.on_message(
    filters.command(commands=["start", "help", "старт", "помощь"])
)
async def start(client: pyrogram.Client, message: types.Message):
    utils.init_db()
    user = utils.db.getUser(message.from_user.id)

    kb = pyroboard.InlineKeyboard(row_width=2)
    kb.add(types.InlineKeyboardButton(
        text=message.tds.get("kbs", "help"), url=f"https://teletype.in/@unneyon/hides-guide-{user[2]}"
    ))
    kb.row(
        types.InlineKeyboardButton(text=message.tds.get("kbs", "change_lang"), callback_data="setlang:choose"),
        types.InlineKeyboardButton(text=message.tds.get("kbs", "developer"), user_id=utils.config['dev_id'])
    )

    await utils.answer(
        message=message,
        sticker=random.choice([
            "CAACAgIAAxkBAAECkihg7Y5tYnlKz9jRe6QCNOyvEZri2wACSQ4AAliyaUuDPYCgY_2GXiAE",
            "CAACAgIAAxkBAAECkilg7Y5tzJPtIX4UMDgYaoxD6zcrogAC8Q0AAvMraEvkpXQDG5qEbyAE",
            "CAACAgIAAxkBAAECkipg7Y5tQk6MZlccqoudX9PEnxPbUwACfBAAAhJpcEuU9SdfdRAPdiAE"
        ])
    )
    return await utils.answer(
        message=message,
        response=message.tds.get("other", "start").format(
            username=client.me.username
        ),
        reply_markup=kb
    )


@other.on_message(
    filters.command(commands=["setlang", "язык"])
)
async def setlang(client: pyrogram.Client, message: types.Message):
    args = utils.get_args(message)
    if args and args[0] in utils.config['langs']:
        utils.db.save("UPDATE users SET lang = ? WHERE id = ?", args[0], message.from_user.id)
        message.tds = utils.translates.TDS(message.from_user.id)
        return await utils.answer(
            message, message.tds.get("other", "lang_saved")
        )
    
    kb = pyroboard.InlineKeyboard(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang:ru"),
        types.InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang:en"),
        types.InlineKeyboardButton(text="🇺🇦 Українська", callback_data="setlang:ua")
    )
    await utils.answer(
        message, message.tds.get("other", "choose_lang"),
        reply_markup=kb
    )


@other.on_callback_query(
    filters.startswith("setlang:")
)
async def setlangCB(client: pyrogram.Client, query: types.CallbackQuery):
    lang = query.data.split(":")[1]
    out = query.tds.get("other", "choose_lang")
    if lang in utils.config['langs']:
        utils.db.save("UPDATE users SET lang = ? WHERE id = ?", lang, query.from_user.id)
        query.tds = utils.translates.TDS(query.from_user.id)
        out = query.tds.get("other", "lang_saved")

    kb = pyroboard.InlineKeyboard(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang:ru"),
        types.InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang:en"),
        types.InlineKeyboardButton(text="🇺🇦 Українська", callback_data="setlang:ua")
    )
    return await utils.edit(
        query.message, out,
        reply_markup=kb
    )


@other.on_message(
    filters.command(commands=["uid", "id", "айди", "ид"])
)
async def getUID(client: pyrogram.Client, message: types.Message):
    uid = await utils.getID(message)
    string = message.tds.get("other", "uid")
    if uid < 1:
        uid = message.from_user.id
        string = message.tds.get("other", "your_id")

    await utils.answer(
        message,
        string.format(uid=uid)
    )
    


@other.on_message(
    filters.command(commands=["ping", "пинг"])
)
async def ping(client: pyrogram.Client, message: types.Message):
    ev = (datetime.datetime.now() - message.date).microseconds / 1000
    s = datetime.datetime.now()
    msg = await utils.answer(
        message, "🍪"
    )

    sapi = datetime.datetime.now()
    await client.get_chat(message.chat.id)
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    kb = pyrogram.types.InlineKeyboardMarkup([[
        pyrogram.types.InlineKeyboardButton(
            text=message.tds.get("kbs", "retry"), callback_data="ping"
        )
    ]])

    await utils.edit(
        msg,
        message.tds.get("other", "ping").format(
            event=int(ev),
            took=round((datetime.datetime.now()-s).microseconds/1000, 2), api=eapi,
            uptime=str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))
        ),
        reply_markup=kb
    )


@other.on_callback_query(
    filters.startswith("ping")
)
async def pingCB(client: pyrogram.Client, query: types.CallbackQuery):
    s = datetime.datetime.now()
    msg = await utils.edit(
        query.message, "🍪"
    )
    ev = (datetime.datetime.now() - msg.date).microseconds / 1000

    sapi = datetime.datetime.now()
    await client.get_chat(msg.chat.id)
    eapi = round((datetime.datetime.now()-sapi).microseconds/1000, 2)

    kb = pyrogram.types.InlineKeyboardMarkup([[
        pyrogram.types.InlineKeyboardButton(
            text=query.tds.get("kbs", "retry"), callback_data="ping"
        )
    ]])

    await utils.edit(
        msg,
        query.tds.get("other", "ping").format(
            event=int(ev),
            took=round((datetime.datetime.now()-s).microseconds/1000, 2), api=eapi,
            uptime=str(datetime.timedelta(seconds=round(time.perf_counter() - utils.init_ts)))
        ),
        reply_markup=kb
    )