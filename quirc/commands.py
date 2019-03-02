
# Quirc IRC Client
# Copyright (C) 2019  Daniel Hetrick

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from quirc.common import *

from quirc.script import QuircScriptThread
from quirc.script import Script

def help_commands(txt,htype,gui,parent):

	tokens = txt.split()

	if len(tokens) >= 1 and tokens[0].lower() == "/help":
		if len(tokens) == 1:
			# list all commands
			for c in COMMAND_HELP_LIST:
				d = system_message(parent.system_color,parent.background_color,parent.system_styles,f"<i>{c}</i>")
				gui.writeText(d)
			if htype == HELP_TYPE_CHANNEL:
				for c in COMMAND_CHANNEL_HELP_LIST:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,f"<i>{c}</i>")
					gui.writeText(d)
			if htype == HELP_TYPE_SERVER:
				for c in COMMAND_SERVER_HELP_LIST:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,f"<i>{c}</i>")
					gui.writeText(d)
			if htype == HELP_TYPE_USER:
				for c in COMMAND_USER_HELP_LIST:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,f"<i>{c}</i>")
					gui.writeText(d)
			return True
		if len(tokens) == 2:
			c = tokens[1].lower()
			if c in COMMAND_HELP:
				d = system_message(parent.system_color,parent.background_color,parent.system_styles,COMMAND_HELP[c])
				gui.writeText(d)
				return True
			if htype == HELP_TYPE_CHANNEL:
				if c in COMMAND_CHANNEL_HELP:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,COMMAND_CHANNEL_HELP[c])
					gui.writeText(d)
					return True
			if htype == HELP_TYPE_SERVER:
				if c in COMMAND_SERVER_HELP:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,COMMAND_SERVER_HELP[c])
					gui.writeText(d)
					return True
			if htype == HELP_TYPE_USER:
				if c in COMMAND_USER_HELP:
					d = system_message(parent.system_color,parent.background_color,parent.system_styles,COMMAND_USER_HELP[c])
					gui.writeText(d)
					return True
			d = system_message(parent.system_color,parent.background_color,parent.system_styles,f"Command \"{tokens[1]}\" not found.")
			gui.writeText(d)
			return True

	return False

def shared_commands(txt,client,gui,parent):

	tokens = txt.split()

	#self.connection.send_items('NAMES', channel)

	if len(tokens) >= 1 and tokens[0].lower() == "/script":
		if len(tokens) >= 2:
			tokens.pop(0)
			for f in tokens:
				parent.cmd_qscript = QuircScriptThread(client,parent,f,RUN_SCRIPT)
				parent.cmd_qscript.closewindow.connect(parent.script_close_window)
				parent.cmd_qscript.channelmsg.connect(parent.script_channel_msg)
				parent.cmd_qscript.errormsg.connect(parent.script_error_msg)
				parent.cmd_qscript.start()
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /script FILENAME")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/raw":
		if len(tokens) >= 2:
			tokens.pop(0)
			cmd = tokens.pop(0)
			client.send_items(cmd.upper(),*tokens)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /ram CMD")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/nick":
		if len(tokens) == 2:
			newnick = tokens[1]
			oldnick = parent.nickname
			client.nick(newnick)
			parent.nickname = newnick
			parent.refresh_all_users()
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /nick NEW_NICKNAME")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/join":
		if len(tokens) == 2:
			channel = tokens[1]
			client.join(channel)
			return True
		if len(tokens) == 3:
			channel = tokens[1]
			key = tokens[2]
			client.join(channel,key)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /join CHANNEL [KEY]")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/part":
		if len(tokens) == 2:
			channel = tokens[1]
			client.part(channel)
			parent.skipNextError = True
			parent.partChannel(channel)
			return True
		if len(tokens) == 3:
			channel = tokens[1]
			msg = tokens[2]
			client.part(channel,msg)
			parent.skipNextError = True
			parent.partChannel(channel)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /part CHANNEL [MESSAGE]")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/msg":
		if len(tokens) >= 3:
			tokens.pop(0)
			target = tokens.pop(0)
			msg = " ".join(tokens)
			client.privmsg(target,msg)
			msg = f"->{target}: {msg}"
			d = chat_message(parent.myusername_color,parent.background_color,parent.chat_color,parent.nickname,msg,parent.maxnicklength)
			gui.writeText(d)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /msg TARGET MESSAGE")
		gui.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/notice":
		if len(tokens) >= 3:
			tokens.pop(0)
			target = tokens.pop(0)
			msg = " ".join(tokens)
			client.notice(target,msg)
			msg = f"->{target}: {msg}"
			d = chat_message(parent.myusername_color,parent.background_color,parent.notice_color,parent.nickname,msg,parent.maxnicklength)
			gui.writeText(d)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /notice TARGET MESSAGE")
		gui.writeText(d)
		return True

	return False

def channel_commands(txt,channel,client,gui,parent):

	tokens = txt.split()

	if len(tokens) >= 1 and tokens[0].lower() == "/me":
		if len(tokens) >= 2:
			tokens.pop(0)
			msg = " ".join(tokens)
			client.action(channel,msg)
			d = action_message(parent.action_color,parent.background_color,parent.nickname,msg)
			gui.writeText(d)
			return True
		d = system_message(parent.system_color,parent.background_color,parent.system_styles,"USAGE: /me MESSAGE")
		gui.writeText(d)
		return True

	return False
