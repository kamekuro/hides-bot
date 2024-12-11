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

AnyText = typing.Union[typing.Tuple[str, ...], typing.List[str], str]

def AnyTextToList(t: "AnyText") -> typing.Union[typing.Tuple[str, ...], typing.List[str]]:
    return (t,) if isinstance(t, str) else t


def startswith(pattern: str, ignore_case: bool = True):
    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message):
            value = update.text or update.caption
        elif isinstance(update, types.CallbackQuery):
            value = update.data
        elif isinstance(update, types.InlineQuery):
            value = update.query
        elif isinstance(update, types.ChosenInlineResult):
            value = update.query
        else:
            raise ValueError(f"Regex filter doesn't work with {type(update)}")

        if ignore_case:
            value = value.lower()

        user = utils.db.getUser(update.from_user.id)
        if not user:
            lang = "ru"
            if update.from_user.language_code in utils.config['langs']:
                lang = update.from_user.language_code
                user = utils.db.regUser(update.from_user.id, lang=lang)
        update.tds = utils.translates.TDS(update.from_user.id)
        return bool(value.startswith(pattern))

    return filters.create(
        func,
        "StartswithFilter",
        pattern=pattern,
        ignore_case=ignore_case
    )


def text(pattern: str):
    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message):
            value = update.text or update.caption
        elif isinstance(update, types.CallbackQuery):
            value = update.data
        elif isinstance(update, types.InlineQuery):
            value = update.query
        elif isinstance(update, types.ChosenInlineResult):
            value = update.query
        else:
            raise ValueError(f"TextFilter doesn't work with {type(update)}")

        user = utils.db.getUser(update.from_user.id)
        if not user:
            lang = "ru"
            if update.from_user.language_code in utils.config['langs']:
                lang = update.from_user.language_code
                user = utils.db.regUser(update.from_user.id, lang=lang)
        update.tds = utils.translates.TDS(update.from_user.id)
        return bool(value == pattern)

    return filters.create(
        func,
        "TextFilter",
        p=pattern
    )


def all():
    async def func(flt, _, update: types.Update):
        user = utils.db.getUser(update.from_user.id)
        if not user:
            lang = "ru"
            if update.from_user.language_code in utils.config['langs']:
                lang = update.from_user.language_code
                user = utils.db.regUser(update.from_user.id, lang=lang)
        update.tds = utils.translates.TDS(update.from_user.id)

        return True

    return filters.create(
        func,
        "AllFilter"
    )


def status(status: int, can_use_in_chats: bool = False):
    async def func(flt, _, update: types.Update):
        if isinstance(update, types.Message):
            if not can_use_in_chats:
                if update.chat.type != pyrogram.enums.ChatType.PRIVATE:
                    return False
        uid = update.from_user.id
        user = utils.db.getUser(uid)
        if not user:
            lang = "ru"
            if update.from_user.language_code in utils.config['langs']:
                lang = update.from_user.language_code
                user = utils.db.regUser(uid, lang=lang)
        update.tds = utils.translates.TDS(uid)

        out = update.tds.get("utils", "u_need_admin").format(status=status)

        if user[1] < status:
            if isinstance(update, types.Message):
                await utils.answer(update, out)
            elif isinstance(update, types.InlineQuery):
                pass
            else:
                await update.answer(utils.remove_html(out))
        return bool(user[1] >= status)

    return filters.create(
        func,
        "StatusFilter",
        status=status,
        can_use_in_chats=can_use_in_chats
    )


def command(commands: typing.Union[str, typing.List[str]], prefixes: typing.Union[str, typing.List[str]] = ["!", "/"], case_sensitive: bool = False):
    command_re = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")

    async def func(flt, client: pyrogram.Client, message: types.Message):
        username = client.me.username or ""
        text = message.text or message.caption
        message.command = None

        user = utils.db.getUser(message.from_user.id)
        if not user:
            lang = "ru"
            if message.from_user.language_code in utils.config['langs']:
                lang = message.from_user.language_code
                user = utils.db.regUser(message.from_user.id, lang=lang)
        message.tds = utils.translates.TDS(message.from_user.id)

        if not text:
            return False

        for prefix in flt.prefixes:
            if not text.startswith(prefix):
                continue

            without_prefix = text[len(prefix):]

            for cmd in flt.commands:
                if not re.match(rf"^(?:{cmd}(?:@?{username})?)(?:\s|$)", without_prefix,
                                flags=re.IGNORECASE if not flt.case_sensitive else 0):
                    continue

                without_command = re.sub(rf"{cmd}(?:@?{username})?\s?", "", without_prefix, count=1,
                                         flags=re.IGNORECASE if not flt.case_sensitive else 0)

                message.command = [cmd] + [
                    re.sub(r"\\([\"'])", r"\1", m.group(2) or m.group(3) or "")
                    for m in command_re.finditer(without_command)
                ]

                return True

        return False

    commands = commands if isinstance(commands, list) else [commands]
    commands = {c if case_sensitive else c.lower() for c in commands}

    prefixes = [] if prefixes is None else prefixes
    prefixes = prefixes if isinstance(prefixes, list) else [prefixes]
    prefixes = set(prefixes) if prefixes else {""}

    return filters.create(
        func,
        "CommandFilter",
        commands=commands,
        prefixes=prefixes,
        case_sensitive=case_sensitive
    )