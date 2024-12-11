#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

from aiocache import Cache
from aiocache.serializers import JsonSerializer

import pyrogram
import pyrogram_patch

import utils

client = pyrogram.Client(
	name="hides-bot",
	api_id=utils.config['app']['id'],
	api_hash=utils.config['app']['hash'],
	app_version=f"👀 Spoilers Bot v{utils.config['version']}",
	bot_token=utils.config['token'],
	parse_mode=pyrogram.enums.ParseMode.HTML
)

patch = pyrogram_patch.patch(client)


cache = Cache(Cache.MEMORY, serializer=JsonSerializer())