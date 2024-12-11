#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import json
from .tools import db, config


class TDS:
	def __init__(self, user_id: int = None, lang: str = "ru"):
		if user_id:
			self.user = db.getUser(int(user_id))
			self.lang = self.user[2]
		else:
			self.lang = lang if lang in config['langs'] else "ru"
		self.dict = json.loads(open(f"translates/{self.lang}.json", "r", encoding="utf-8").read())
		self.default_dict = json.loads(open(f"translates/ru.json", "r", encoding="utf-8").read())


	def get(self, module: str, key: str):
		string = self.dict.get(module, None)
		if string:
			string = string.get(key, None)
			if not string:
				string = self.default_dict.get(module, None)
				if string:
					string = string.get(key, None)
		if not string:
			string = self.default_dict.get(module, None)
			if string:
				string = string.get(key, None)
		return string if string else "Unknown string"