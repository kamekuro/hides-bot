#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import datetime
import logging
import pytz
import time
import uuid

import pyrogram
import pyroboard
import pyrogram_patch
from pyrogram import types
from pyrogram_patch.router import Router

import utils
from dispatch import filters
from loader import cache


hides = Router()
hides.name = "hides"
logger = logging.getLogger(__name__)


@hides.on_inline_query(filters.text(""))
async def guide(client: pyrogram.Client, query: types.InlineQuery):
    await query.answer(
        results=[types.InlineQueryResultArticle(
            title=query.tds.get("hides", "guide_title"),
            input_message_content=types.InputTextMessageContent(
                message_text=query.tds.get("hides", "guide").format(me=client.me.username)
            ),
            description=""
        )],
        cache_time=0
    )


@hides.on_inline_query(filters.all())
async def sendHide(client: pyrogram.Client, query: types.InlineQuery):
    args = query.query
    text = list(reversed(query.query.split(' ')))
    users = []

    for i in list(reversed(args.split())):
        if not i.startswith("@") and not i.isdigit():
            break
        if i.startswith("@"):
            uid = await utils.getIdByText(client, str(i))
            if uid < 1:
                users.append(str(i)[1:])
                text.remove(str(i))
                continue
        elif i.isdigit():
            try:
                us = await client.get_users(int(i))
                uid = us.id
            except:
                pass
        if uid not in users:
            pass
        elif i.startswith("@") and str(i)[1:] not in users:
            pass
        else:
            continue
        users.append(uid)
        text.remove(str(i))

    text = ' '.join(list(reversed(text)))

    async def genObj(text, users, from_id):
        rand_uid = uuid.uuid4().hex
        if await cache.get(rand_uid):
            return await genObj(text, users, from_id)
        await cache.set(rand_uid, {
            "text": text,
            "users": users,
            "from_id": from_id
        }, ttl=(60*60)*1); return rand_uid
    rand_uuid = await genObj(text, users, query.from_user.id)

    users_pushes = []
    for u in users:
        if str(u).isdigit():
            try:
                uu = await client.get_users(u)
            except:
                users_pushes.append(f"{'' if str(u).isdigit() else '@'}{str(u)}"); continue
            users_pushes.append(f"@{uu.username}")
        else:
            users_pushes.append(f"@{str(u)}")

    if len(users) > 0:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    title=query.tds.get("hides", "send_hide").format(
                        us=', '.join(users_pushes)
                    ),
                    input_message_content=types.InputTextMessageContent(
                        message_text=query.tds.get("hides", "hide").format(
                            us=', '.join(users_pushes)
                        )
                    ),
                    description="",
                    reply_markup=types.InlineKeyboardMarkup([[
                        types.InlineKeyboardButton(
                            text=query.tds.get("kbs", "open_hide"),
                            callback_data=f"open_hide:{rand_uuid}"
                        )
                    ]]),
                    thumb_url="https://static.unneyon.ru/hides/hide.png"
                ),
                types.InlineQueryResultArticle(
                    title=query.tds.get("hides", "send_except").format(
                        us=', '.join(users_pushes)
                    ),
                    input_message_content=types.InputTextMessageContent(
                        message_text=query.tds.get("hides", "except").format(
                            us=', '.join(users_pushes)
                        )
                    ),
                    description="",
                    reply_markup=types.InlineKeyboardMarkup([[
                        types.InlineKeyboardButton(
                            text=query.tds.get("kbs", "open_hide"),
                            callback_data=f"open_except:{rand_uuid}"
                        )
                    ]]),
                    thumb_url="https://static.unneyon.ru/hides/except.png"
                )
            ],
            cache_time=0
        )
    
    else:
        await query.answer(
            results=[
                types.InlineQueryResultArticle(
                    title=query.tds.get("hides", "send_spoiler"),
                    input_message_content=types.InputTextMessageContent(
                        message_text=query.tds.get("hides", "spoiler")
                    ),
                    description="",
                    reply_markup=types.InlineKeyboardMarkup([[
                        types.InlineKeyboardButton(
                            text=query.tds.get("kbs", "open_hide"),
                            callback_data=f"open_spoiler:{rand_uuid}"
                        )
                    ]]),
                    thumb_url="https://static.unneyon.ru/hides/spoiler.png"
                )
            ],
            cache_time=0
        )


@hides.on_callback_query(
    filters.startswith("open_spoiler:")
)
async def openHide(client: pyrogram.Client, query: types.CallbackQuery):
    rand_uuid = query.data.split(":")[1]
    hide = await cache.get(rand_uuid)
    if not hide:
        return await query.answer(
            query.tds.get("hides", "hide_is_dead"),
            show_alert=True
        )

    return await query.answer(
        hide.get(
            "text",
            query.tds.get("hides", "hide_is_dead")
        ).format(
            lang=query.from_user.language_code,
            username=f"@{query.from_user.id}" if not query.from_user.username else f"@{query.from_user.username}",
            uid=str(query.from_user.id),
            date=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y"),
            time=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%H:%M"),
            name=query.from_user.full_name,
            first_name=query.from_user.first_name,
            last_name='' if query.from_user.last_name is None else query.from_user.last_name,
        ),
        show_alert=True
    )


@hides.on_callback_query(
    filters.startswith("open_hide:")
)
async def openHide(client: pyrogram.Client, query: types.CallbackQuery):
    rand_uuid = query.data.split(":")[1]
    hide = await cache.get(rand_uuid)
    if not hide:
        return await query.answer(
            query.tds.get("hides", "hide_is_dead"),
            show_alert=True
        )

    if len(hide.get("users", [])) == 0:
        return await query.answer(
            hide.get(
                "text",
                query.tds.get("hides", "hide_is_dead")
            ),
            show_alert=True
        )

    if query.from_user.id != hide.get("from_id", 0):
        if (query.from_user.username not in hide.get("users", [])) and (query.from_user.id not in hide.get("users", [])):
            return await query.answer(query.tds.get("hides", "not4u"), show_alert=True)

    return await query.answer(
        hide.get(
            "text",
            query.tds.get("hides", "hide_is_dead")
        ).format(
            lang=query.from_user.language_code,
            username=f"@{query.from_user.id}" if not query.from_user.username else f"@{query.from_user.username}",
            uid=str(query.from_user.id),
            date=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y"),
            time=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%H:%M"),
            name=query.from_user.full_name,
            first_name=query.from_user.first_name,
            last_name='' if query.from_user.last_name is None else query.from_user.last_name,
        ),
        show_alert=True
    )


@hides.on_callback_query(
    filters.startswith("open_except:")
)
async def openHide(client: pyrogram.Client, query: types.CallbackQuery):
    rand_uuid = query.data.split(":")[1]
    hide = await cache.get(rand_uuid)
    if not hide:
        return await query.answer(
            query.tds.get("hides", "hide_is_dead"),
            show_alert=True
        )

    if len(hide.get("users", [])) == 0:
        return await query.answer(
            hide.get(
                "text",
                query.tds.get("hides", "hide_is_dead")
            ),
            show_alert=True
        )

    if query.from_user.id != hide.get("from_id", 0):
        if (query.from_user.username in hide.get("users", [])) or (query.from_user.id in hide.get("users", [])):
            return await query.answer(query.tds.get("hides", "not4u"), show_alert=True)

    return await query.answer(
        hide.get(
            "text",
            query.tds.get("hides", "hide_is_dead")
        ).format(
            lang=query.from_user.language_code,
            username=f"@{query.from_user.id}" if not query.from_user.username else f"@{query.from_user.username}",
            uid=str(query.from_user.id),
            date=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y"),
            time=datetime.datetime.now(tz=pytz.timezone("Europe/Moscow")).strftime("%H:%M"),
            name=query.from_user.full_name,
            first_name=query.from_user.first_name,
            last_name='' if query.from_user.last_name is None else query.from_user.last_name,
        ),
        show_alert=True
    )