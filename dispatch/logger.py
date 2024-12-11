#          █  █ █▄ █ █▄ █ █▀▀ ▀▄▀ █▀█ █▄ █
#          ▀▄▄▀ █ ▀█ █ ▀█ ██▄  █  █▄█ █ ▀█ ▄
#                © Copyright 2024
#
#            👤 https://t.me/unneyon
#
# 🔒 Licensed under the GNU GPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

import contextlib
import html
import inspect
import json
import re
import os
import traceback
import typing
import pyrogram

from utils import config



def find_caller(
	stack: typing.Optional[typing.List[inspect.FrameInfo]] = None,
) -> typing.Any:
	"""
	Attempts to find command in stack
	:param stack: Stack to search in
	:return: Command-caller or None
	"""
	caller = next(
		(
			frame_info
			for frame_info in stack or inspect.stack()
			if hasattr(frame_info, "function")
		),
		None,
	)

	if not caller:
		return next(
			(
				frame_info.frame.f_locals["func"]
				for frame_info in stack or inspect.stack()
				if hasattr(frame_info, "function")
				and frame_info.function == "future_dispatcher"
				and (
					"CommandDispatcher"
					in getattr(getattr(frame_info, "frame", None), "f_globals", {})
				)
			),
			None,
		)

	return next(
		(
			getattr(cls_, caller.function, None)
			for cls_ in caller.frame.f_globals.values()
		),
		None,
	)



class CustomException:
	def __init__(
		self,
		message: str,
		local_vars: str,
		full_stack: str,
		sysinfo: typing.Optional[
			typing.Tuple[object, Exception, traceback.TracebackException]
		] = None,
	):
		self.message = message
		self.local_vars = local_vars
		self.full_stack = full_stack
		self.sysinfo = sysinfo
		self.debug_url = None


	@classmethod
	def from_exc_info(
		cls,
		exc_type: object,
		exc_value: Exception,
		tb: traceback.TracebackException,
		stack: typing.Optional[typing.List[inspect.FrameInfo]] = None,
	) -> "CustomException":
		def to_hashable(dictionary: dict) -> dict:
			dictionary = dictionary.copy()
			for key, value in dictionary.items():
				if isinstance(value, dict):
					dictionary[key] = to_hashable(value)
				else:
					try:
						if (
							getattr(getattr(value, "__class__", None), "__name__", None)
							== "Database"
						):
							dictionary[key] = "<Database>"
						elif isinstance(
							value,
							(pyrogram.Client),
						):
							dictionary[key] = f"<{value.__class__.__name__}>"
						elif len(str(value)) > 512:
							dictionary[key] = f"{str(value)[:512]}..."
						else:
							dictionary[key] = str(value)
					except Exception:
						dictionary[key] = f"<{value.__class__.__name__}>"

			return dictionary

		full_stack = traceback.format_exc().replace(
			"Traceback (most recent call last):\n", ""
		)

		line_regex = r'  File "(.*?)", line ([0-9]+), in (.+)'

		def format_line(line: str) -> str:
			filename_, lineno_, name_ = re.search(line_regex, line).groups()
			with contextlib.suppress(Exception):
				filename_ = os.path.basename(filename_)

			return (
				f"👉 <code>{html.escape(filename_)}:{lineno_}</code> <b>in</b>"
				f" <code>{html.escape(name_)}</code>"
			)

		filename, lineno, name = next(
			(
				re.search(line_regex, line).groups()
				for line in reversed(full_stack.splitlines())
				if re.search(line_regex, line)
			),
			(None, None, None),
		)

		full_stack = "\n".join(
			[
				(
					format_line(line)
					if re.search(line_regex, line)
					else f"<code>{html.escape(line)}</code>"
				)
				for line in full_stack.splitlines()
			]
		)

		with contextlib.suppress(Exception):
			filename = os.path.basename(filename)

		caller = find_caller(stack or inspect.stack())
		cause_mod = (
			"🪬 <b>Possible cause: method"
			f" </b><code>{html.escape(caller.__name__)}</code><b> of module"
			f" </b><code>{html.escape(caller.__self__.__class__.__name__)}</code>\n"
			if caller and hasattr(caller, "__self__") and hasattr(caller, "__name__")
			else ""
		)

		return CustomException(
			message=(
				f"<b>🚫 Error!</b>\n{cause_mod}\n<b>🗄 Where:</b>"
				f" <code>{html.escape(filename)}:{lineno}</code><b>"
				f" in </b><code>{html.escape(name)}</code>\n<b>❓ What:</b>"
				f" <code>{html.escape(''.join(traceback.format_exception_only(exc_type, exc_value)).strip())}</code>"
			),
			local_vars=(
				f"<code>{html.escape(json.dumps(to_hashable(tb.tb_frame.f_locals), indent=4))}</code>"
			),
			full_stack=full_stack,
			sysinfo=(exc_type, exc_value, tb),
		)