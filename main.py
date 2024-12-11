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
import os; os.system("clear")
if not os.path.exists('config.json'):
	exit("\033[31mОтсутствует файл\033[0m \033[36mconfig.json\033[31m!\033[0m")
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import pyrogram
import pyrogram_patch
from pyrogram_patch.fsm.storages import MemoryStorage

import utils; utils.checkConfig()
from commands import routers
from loader import client, patch
from utils import middlewares

logging.basicConfig(
	level=logging.INFO,
	format='[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d]\n>>> %(message)s\n',
	filename='logs.log',
	filemode='w+'
)

patch.include_middleware(middlewares.RegUser())

utils.init_db()
utils.printMe()
print("\033[36mИнформация по роутерам:\033[0m")
for router in routers:
	if utils.config['commands'][router.name]:
		patch.include_router(router)
		print(f"\033[32m  • Роутер [{router.name}] успешно добавлен!\033[0m")
		continue
	print(f"\033[31m  • Роутер [{router.name}] отключен.\033[0m")


scheduler = AsyncIOScheduler()
scheduler.add_job(utils.sendBackup, "interval", seconds=3600)

print(f"\033[36mБот [Spoilers Bot v{utils.config['version']}] успешно запущен!\033[0m")
patch.set_storage(MemoryStorage())
scheduler.start()
client.run()