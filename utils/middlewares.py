#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import logging
import io

import pyrogram
import pyrogram_patch
from pyrogram import types
from pyrogram_patch.middlewares.middleware_types import OnUpdateMiddleware, OnRawUpdateMiddleware, OnMessageMiddleware
from pyrogram_patch.middlewares import PatchHelper

import utils


class RegUser(OnMessageMiddleware):
	def __init__(self, *args, **kwargs):
		pass

	async def __call__(self, message: types.Message, client: pyrogram.Client, patch_helper: PatchHelper):
		uid = message.from_user.id
		aus = utils.db.getAllUsers()
		user = utils.db.getUser(uid)
		lang = "ru"
		if message.from_user.language_code == "uk":
			message.from_user.language_code = "ua"
		if message.from_user.language_code in utils.config['langs']:
			lang = message.from_user.language_code

		if not user:
			user = utils.db.regUser(uid, lang=lang)

		return