#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import sqlite3
import utils


class DataBase():
	def __init__(self, filename: str = "db.db"):
		self.db = sqlite3.connect(filename)
		self.cursor = self.db.cursor()


	def close(self):
		self.db.close()


	def recvs(self, f, *args):
		self.cursor.execute(f, args)
		return self.cursor.fetchall()

	def save(self, f, *args):
		self.cursor.execute(f, args)
		return self.db.commit()


	def getAllTables(self):
		t = self.recvs("SELECT name FROM sqlite_master WHERE type = 'table'")
		return [i[0] for i in t]

	def getTable(self, table: str):
		tables = self.getAllTables()
		if table not in tables:
			return None
		return self.recvs(f"PRAGMA table_info({table})")


	def regUser(self, uid: int, status: int = 0, lang: str = "ru"):
		u = self.getUser(uid)
		if not u:
			self.save(f"""INSERT INTO users (id, status, lang) VALUES (?, ?, ?)""", uid, status, lang)
			u = self.getUser(uid)
		return u

	def getUser(self, uid: int):
		user = self.recvs(f"SELECT * FROM users WHERE id = ?", uid)
		return None if len(user) == 0 else user[0]

	def getAllUsers(self):
		return self.recvs(f"SELECT * FROM users")


	def regChat(self, id: int, is_admin: bool = False):
		c = self.getChat(id)
		if not c:
			self.save(
				f"""INSERT INTO chats (id, is_admin) VALUES (?, ?)""",
				id, int(is_admin)
			)
			c = self.getChat(id)
		return c

	def getChat(self, id: int):
		chat = self.recvs(f"SELECT * FROM chats WHERE id = ?", id)
		return None if len(chat) == 0 else chat[0]

	def getAllChats(self):
		return self.recvs(f"SELECT * FROM chats")