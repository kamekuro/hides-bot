#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import asyncio
import contextlib
import logging
import os
import sys
from meval import meval

import pyrogram
import pyrogram_patch
from pyrogram import types
from pyrogram_patch.router import Router

import utils
from dispatch import filters
from dispatch.logger import CustomException



admin = Router()
admin.name = "admin"
logger = logging.getLogger(__name__)

locs = locals()

async def getattrs(client, message):
	e = locs
	e["client"] = client
	e["c"] = client
	e["message"] = message
	e["m"] = message
	e["reply"] = message.reply_to_message
	e["r"] = message.reply_to_message
	return {**e}



@admin.on_message(
	filters.command(commands=["eval", "e", "евал", "ебал", "е"], prefixes=["!", "/", "~"])
	& filters.status(2)
)
async def eval(client: pyrogram.Client, message: types.Message):
	args = utils.get_raw_args(message)
	code = f'<pre language="python">{str(args).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</pre>'
 
	try: 
		result = await meval( 
			args, 
			globals(), 
			**await getattrs(client, message)
		) 
	except Exception: 
		exc = CustomException.from_exc_info(*sys.exc_info()) 
		full_err = '\n'.join(exc.full_stack.splitlines()[:-1]) 
 
		await utils.answer( 
			message,
			message.tds.get("admin", "code").format(code=code) + message.tds.get("admin", "python_err").format(
				stack=utils.remove_html(str(full_err)).replace('&', ' &amp;').replace('<', '&lt;').replace('>', '&gt;'),
				error=utils.remove_html(str(exc.full_stack.splitlines()[-1])).replace('&', ' &amp;').replace('<', '&lt;').replace('>', '&gt;')
			)
		) 
		return

	if callable(getattr(result, "stringify", None)):
		with contextlib.suppress(Exception):
			result = str(result.stringify())
	else:
		result = str(result)

	with contextlib.suppress(pyrogram.errors.exceptions.bad_request_400.MessageIdInvalid):
		await utils.answer(
			message,
			message.tds.get("admin", "code").format(code=code) + message.tds.get("admin", "python").format(
				result=str(utils.censor(result)).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
			)
		)



@admin.on_message(
	filters.command(commands=["terminal", "t", "терминал"], prefixes=["!", "/", "~"])
	& filters.status(2)
)
async def terminal(client: pyrogram.Client, message: types.Message):
	args = utils.get_raw_args(message)

	out, err = await (await asyncio.create_subprocess_shell(
		args,
		stdout=asyncio.subprocess.PIPE,
		stderr=asyncio.subprocess.PIPE,
		cwd=os.path.abspath(os.path.dirname(os.path.abspath("main.py")))
	)).communicate()

	out_msg = message.tds.get("admin", "terminal").format(cmd=args)
	if out.decode():
		out_msg += message.tds.get("admin", "shell_out").format(out=out.decode())
	if err.decode():
		out_msg += message.tds.get("admin", "shell_err").format(err=err.decode())

	await utils.answer(
		message,
		out_msg
	)



@admin.on_message(
	filters.command(commands=["status", "статус"], prefixes=["!", "/", "~"])
	& filters.status(2)
)
async def chStatus(client: pyrogram.Client, message: types.Message):
	args = utils.get_args(message)
	from_user = utils.db.regUser(message.from_user.id)
	uid = await utils.getID(message)
	status = None
	if uid < 1:
		return await utils.answer(
			message, message.tds.get("utils", "no_user")
		)
	user = utils.db.getUser(uid)
	if not user:
		user = utils.db.regUser(uid)

	if message.reply_to_message:
		if len(args) > 0 and str(args[0]).isdigit():
			status = int(args[0])
	else:
		if len(args) > 1 and str(args[1]).isdigit():
			status = int(args[1])

	if status is None:
		return await utils.answer(
			message,
			message.tds.get("admin", "current_status").format(
				uid=user[0],
				status=utils.config['statuses'].get(str(user[1]))
			)
		)
	if status == 2 or user[0] == message.from_user.id or user[1] >= from_user[1]:
		return await client.send_sticker(
			message.chat.id,
			"CAACAgIAAxkBAANlZgxcxNiK7_5qf162sKU7DQzZ_xEAAg9xAAKezgsAAQgdBUWPRJL6HgQ"
		)

	utils.db.save(f"UPDATE users SET status = {int(status)} WHERE id = {user[0]}")
	await utils.answer(
		message,
		message.tds.get("admin", "status_changed").format(
			uid=user[0],
			old=utils.config['statuses'].get(str(user[1])),
			new=utils.config['statuses'].get(str(status))
		)
	)

	name = message.from_user.first_name
	if message.from_user.last_name:
		name += f" {message.from_user.last_name}"
	name += f" [<code>{message.from_user.id}</code>]"
	await utils.answer(
		message,
		f"📂✏ <b>{name} изменил статус пользователя [<code>{user[0]}</code>]:</b> [" \
		f"{utils.config['statuses'].get(str(user[1]))}] -> [{utils.config['statuses'].get(str(status))}]",
		False,
		utils.config['admin_chat'] if utils.config['admin_chat'] else utils.config['dev_id']
	)