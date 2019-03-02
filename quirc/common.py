
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

import sys
import os
import json
import re
import platform

# Globally load in Quirc's resource file
globals()["quirc.resources"] = __import__("quirc.resources")

import quirc.colour

APPLICATION_NAME = "Quirc"
APPLICATION_VERSION = "0.10"
APPLICATION_DESCRIPTION = "Open Source Internet Relay Chat Client"

SCRIPT_VARIABLE_SYMBOL = '$'

RUN_SCRIPT = 0
TEST_SCRIPT = 1

HELP_TYPE_CHANNEL = 0
HELP_TYPE_SERVER = 1
HELP_TYPE_USER = 2
COMMAND_HELP = {
	"nick": "<b>/nick</b> - Changes the nickname to use.",
	"join": "<b>/join</b> - Joins a channel. Append the channel's KEY if one is required.",
	"part": "<b>/part</b> - Leaves a channel. Append a parting message if desired.",
	"msg": "<b>/msg</b> - Sends a private MSG to a TARGET.",
	"notice": "<b>/notice</b> - Sends a notice MSG to a TARGET.",
	"raw": "<b>/raw</b> - Sends a raw MSG to the IRC server. For example, to send a PRIVMSG command, try /raw privmsg TARGET MSG."
}
COMMAND_HELP_LIST = [
	"<b>/nick NEW</b>              -     Changes user nickname to NEW",
	"<b>/join CHANNEL [KEY]</b>    -     Joins CHANNEL",
	"<b>/part CHANNEL [MSG]</b>    -     Leaves CHANNEL",
	"<b>/msg TARGET MSG</b>        -     Sends TARGET a private message MSG",
	"<b>/notice TARGET MSG</b>     -     Sends TARGET a notice MSG",
	"<b>/raw CMD</b>               -     Sends a raw command to the IRC server"
]
COMMAND_CHANNEL_HELP_LIST = [
	"<b>/me MSG</b>                -     Sends a CTCP action MSG to current channel"
]
COMMAND_CHANNEL_HELP = {
	"me": "<b>/me</b> - Sends a CTCP action MSG to current channel."
}
COMMAND_SERVER_HELP_LIST = []
COMMAND_USER_HELP_LIST = [
	"<b>/me MSG</b>                -     Sends a CTCP action MSG to current channel"
]
COMMAND_SERVER_HELP = {}
COMMAND_USER_HELP = {
	"me": "<b>/me</b> - Sends a CTCP action MSG to current channel."
}

HOST_OS = platform.system()
HOST_OS_VERSION = platform.release()
HOST_PLATFORM = platform.platform(aliased=1)

def strip_color_codes(txt):
	txt = txt.replace(IRC_COLOR,'')
	txt = txt.replace(IRC_BOLD,'')
	txt = txt.replace(IRC_ITALIC,'')
	txt = txt.replace(IRC_UNDERLINE,'')
	txt = txt.replace(IRC_REVERSE,'')

	txt = txt.replace(IRC_COLOR_WHITE,'')
	txt = txt.replace(IRC_COLOR_BLACK,'')
	txt = txt.replace(IRC_COLOR_BLUE,'')
	txt = txt.replace(IRC_COLOR_GREEN,'')
	txt = txt.replace(IRC_COLOR_RED,'')
	txt = txt.replace(IRC_COLOR_BROWN,'')
	txt = txt.replace(IRC_COLOR_PURPLE,'')
	txt = txt.replace(IRC_COLOR_ORANGE,'')
	txt = txt.replace(IRC_COLOR_YELLOW,'')
	txt = txt.replace(IRC_COLOR_LIGHT_GREEN,'')
	txt = txt.replace(IRC_COLOR_TEAL,'')
	txt = txt.replace(IRC_COLOR_CYAN,'')
	txt = txt.replace(IRC_COLOR_LIGHT_BLUE,'')
	txt = txt.replace(IRC_COLOR_PINK,'')
	txt = txt.replace(IRC_COLOR_GREY,'')
	txt = txt.replace(IRC_COLOR_LIGHT_GREY,'')

	return txt

IRC_COLOR = chr(3)
IRC_BOLD = chr(2)
IRC_ITALIC = chr(int("0x1D", 0))
IRC_UNDERLINE = chr(int("0x1F", 0))
IRC_REVERSE = chr(16)

IRC_COLOR_WHITE = "00"
IRC_COLOR_BLACK = "01"
IRC_COLOR_BLUE = "02"
IRC_COLOR_GREEN = "03"
IRC_COLOR_RED = "04"
IRC_COLOR_BROWN = "05"
IRC_COLOR_PURPLE = "06"
IRC_COLOR_ORANGE = "07"
IRC_COLOR_YELLOW = "08"
IRC_COLOR_LIGHT_GREEN = "09"
IRC_COLOR_TEAL = "10"
IRC_COLOR_CYAN = "11"
IRC_COLOR_LIGHT_BLUE = "12"
IRC_COLOR_PINK = "13"
IRC_COLOR_GREY = "14"
IRC_COLOR_LIGHT_GREY = "15"

HTML_COLOR_WHITE = "#ffffff"
HTML_COLOR_BLACK = "#000000"
HTML_COLOR_BLUE = "#00007F"
HTML_COLOR_GREEN = "#009300"
HTML_COLOR_RED = "#FF0000"
HTML_COLOR_BROWN = "#7F0000"
HTML_COLOR_PURPLE = "#9C009C"
HTML_COLOR_ORANGE = "#FC7F00"
HTML_COLOR_YELLOW = "#FFFF00"
HTML_COLOR_LIGHT_GREEN = "#00FC00"
HTML_COLOR_TEAL = "#009393"
HTML_COLOR_CYAN = "#00FFFF"
HTML_COLOR_LIGHT_BLUE = "#0000FC"
HTML_COLOR_PINK = "#FF00FF"
HTML_COLOR_GREY = "#7F7F7F"
HTML_COLOR_LIGHT_GREY = "#D2D2D2"

QUIRC_COLOR = "#ff9c00"

DEFAULT_NICKNAME = 'quirc'
DEFAULT_USERNAME = 'quirc'
DEFAULT_REALNAME = 'Quirc IRC Client'

INSTALL_DIRECTORY = sys.path[0]
DATA_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "data")
RESOURCE_DIRECTORY = os.path.join(DATA_DIRECTORY, "resources")
QUIRC_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "quirc")

USER_INFORMATION_FILE = os.path.join(DATA_DIRECTORY, "user.json")
LAST_SERVER_INFORMATION_FILE = os.path.join(DATA_DIRECTORY, "server.json")

MDI_BACKGROUND = os.path.join(RESOURCE_DIRECTORY, "background.png")

INITIAL_WINDOW_WIDTH = 500
INITIAL_WINDOW_HEIGHT = 300

DEFAULT_FONT_SIZE = 8
USERLIST_FONT_SIZE = 10
BIG_FONT_SIZE = 15
HUGE_FONT_SIZE = 20

LINK_USERNAMES_IN_CHAT = True
LINK_URLS_IN_CHAT = True

RESOURCE_STYLE_SHEET = os.path.join(QUIRC_DIRECTORY, "style.qss")
RESOURCE_CHILD_STYLE_SHEET = os.path.join(QUIRC_DIRECTORY, "child.qss")

RESOURCE_SERVER_LIST = os.path.join(QUIRC_DIRECTORY, "servers.txt")

RESOURCE_COMMANDS_DOC_HTML = os.path.join(QUIRC_DIRECTORY, "QScript.html")

RESOURCE_MDI_BACKGROUND = ":/background.png"
RESOURCE_FONT = ":/FiraCode-Regular.ttf"

RESOURCE_ICON_CASCADE = ":/cascade.png"
RESOURCE_ICON_CONNECT = ":/connect.png"
RESOURCE_ICON_DISCONNECT = ":/disconnect.png"
RESOURCE_ICON_HASH = ":/hash.png"
RESOURCE_ICON_QUIRC = ":/quirc.png"
RESOURCE_ICON_TILE = ":/tile.png"
RESOURCE_ICON_USER = ":/user.png"
RESOURCE_ICON_HELP = ":/help.png"
RESOURCE_ICON_RESTART = ":/restart.png"
RESOURCE_ICON_ABOUT = ":/about.png"
RESOURCE_ICON_EXIT = ":/exit.png"
RESOURCE_ICON_SERVER = ":/server.png"
RESOURCE_ICON_SSL = ":/ssl.png"
RESOURCE_ICON_LEAVE = ":/leave.png"
RESOURCE_ICON_CLIPBOARD = ":/clipboard.png"
RESOURCE_ICON_COPYLEFT = ":/copyleft.png"
RESOURCE_ICON_WWW = ":/web.png"
RESOURCE_ICON_BOOKMARK = ":/bookmark.png"

RESOURCE_LOGO_600x200 = ":/logo_600x200.png"
RESOURCE_LOGO_300x100 = ":/logo_300x100.png"
RESOURCE_LOGO_100x33 = ":/logo_100x33.png"

RESOURCE_GPL_LOGO = ":/gpl.png"
RESOURCE_QT_LOGO = ":/qt.png"
RESOURCE_PYTHON_LOGO = ":/python.png"

RESOURCE_IMAGE_COLORS = ":/colors.png"
RESOURCE_IMAGE_EXTERNAL = ":/external.png"
RESOURCE_IMAGE_INVITEONLY = ":/inviteonly.png"
RESOURCE_IMAGE_LIMIT = ":/limit.png"
RESOURCE_IMAGE_LOCKED = ":/locked.png"
RESOURCE_IMAGE_MINUS = ":/minus.png"
RESOURCE_IMAGE_MODERATED = ":/moderated.png"
RESOURCE_IMAGE_NO = ":/no.png"
RESOURCE_IMAGE_NOEXTERNAL = ":/noexternal.png"
RESOURCE_IMAGE_NOLIMIT = ":/nolimit.png"
RESOURCE_IMAGE_NOTSECRET = ":/notsecret.png"
RESOURCE_IMAGE_PLUS = ":/plus.png"
RESOURCE_IMAGE_SECRET = ":/secret.png"
RESOURCE_IMAGE_UNLOCKED = ":/unlocked.png"
RESOURCE_IMAGE_UNMODERATED = ":/unmoderated.png"
RESOURCE_IMAGE_USER = ":/user_circle.png"
RESOURCE_IMAGE_PEN = ":/pen.png"
RESOURCE_IMAGE_RUN = ":/run.png"
RESOURCE_IMAGE_BUG = ":/bug.png"

RESOURCE_IMAGE_FILE = ":/file.png"
RESOURCE_IMAGE_NEWFILE = ":/new_file.png"
RESOURCE_IMAGE_SAVE = ":/save.png"

RESOURCE_IMAGE_UNDO = ":/undo.png"
RESOURCE_IMAGE_REDO = ":/redo.png"
RESOURCE_IMAGE_CUT = ":/cut.png"
RESOURCE_IMAGE_COPY = ":/copy.png"
RESOURCE_IMAGE_PASTE = ":/paste.png"
RESOURCE_IMAGE_FONT = ":/font.png"



MAXIMUM_NICK_DISPLAY_SIZE = 20
T_USER = "!USER!"
T_MESSAGE = "!MESSAGE!"
T_COLOR = "!COLOR!"
T_CCHAT = "!CCHAT!"
T_GRADIENT = "!GRADIENT!"
T_BACKGROUND = "!BACKGROUND!"
CHAT_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: right; vertical-align: top; !GRADIENT!"><font color="!COLOR!">!USER!</font></td>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";">&nbsp;</td>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";"><font color="!CCHAT!">!MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""
ACTION_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: left; vertical-align: top; !GRADIENT!"><font color="!COLOR!"><b>!USER!</b> !MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""
SYSTEM_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";"><font color="!COLOR!">!MESSAGE!</font></td>
	</tr>
  </tbody>
</table>
"""

GRADIENT_LIGHTEN = 0.95

##########################

def inject_www_links(txt,color):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)
	for u in urls:
		#print(urls)
		u = re.sub('<[^<]+?>', '', u)
		# link = f"<a href=\"{u}\"><span style=\"font-style: normal; color: {color}\">{u}</span></a>"
		link = f"<a href=\"{u}\"><span style=\"text-decoration: none; color: {color}\">{u}</span></a>"
		txt = txt.replace(u,link)
		#print(link)
	#print(txt)
	return txt

def chat_message_link(color,background,chat,user,txt,max,link_color):
	if max>MAXIMUM_NICK_DISPLAY_SIZE: max = MAXIMUM_NICK_DISPLAY_SIZE
	# user = pad_nick_link(user,max,link_color)
	user = pad_nick_link(user,max,color)
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_CCHAT,chat)

	# Gradient
	BG = quirc.colour.Color(background)
	LIGHT_COLOR = quirc.colour.Color(color,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace(T_GRADIENT,USER_BACKGROUND_GRADIENT)

	msg = msg.replace(T_BACKGROUND,background)

	return msg

def action_message_link(color,background,user,txt,link_color):
	# user = pad_nick_link(user,0,link_color)
	user = pad_nick_link(user,0,color)
	msg = ACTION_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)

	user = f"<a href=\"{user}\">{user}</a>"

	# Gradient
	BG = quirc.colour.Color(background)
	LIGHT_COLOR = quirc.colour.Color(color,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace(T_GRADIENT,USER_BACKGROUND_GRADIENT)

	return msg

##########################

def chat_message(color,background,chat,user,txt,max):
	if max>MAXIMUM_NICK_DISPLAY_SIZE: max = MAXIMUM_NICK_DISPLAY_SIZE
	user = pad_nick(user,max)
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_CCHAT,chat)

	# Gradient
	BG = quirc.colour.Color(background)
	LIGHT_COLOR = quirc.colour.Color(color,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace(T_GRADIENT,USER_BACKGROUND_GRADIENT)

	msg = msg.replace(T_BACKGROUND,background)

	return msg

def action_message(color,background,user,txt):
	msg = ACTION_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)

	# Gradient
	BG = quirc.colour.Color(background)
	LIGHT_COLOR = quirc.colour.Color(color,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace(T_GRADIENT,USER_BACKGROUND_GRADIENT)

	return msg

def system_message(color,background,styles,txt):

	for s in styles:
		txt = f"<{s}>{txt}</{s}>"

	msg = SYSTEM_TEMPLATE.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_BACKGROUND,background)

	return msg

def pad_nick(nick,size):
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}{nick}"

def pad_nick_link(nick,size,color):
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}<a href=\"{nick}\"><span style=\"font-style: normal; color: {color}; text-decoration: none;\">{nick}</span></a>"



def is_integer(n):
	try:
		int(n)
	except ValueError:
		return False
	return True
	#return isinstance(n, int)

def save_last_server(host,port,password,ssl):
	sinfo = {
			"host": host,
			"port": port,
			"password": password,
			"ssl": ssl
		}
	with open(LAST_SERVER_INFORMATION_FILE, "w") as write_data:
		json.dump(sinfo, write_data)

def get_last_server():
	if os.path.isfile(LAST_SERVER_INFORMATION_FILE):
		with open(LAST_SERVER_INFORMATION_FILE, "r") as read_server:
			data = json.load(read_server)
			return data
	else:
		si = {
			"host": '',
			"port": '',
			"password": '',
			"ssl": False
		}
		return si

def save_user_information(udata):
	with open(USER_INFORMATION_FILE, "w") as write_data:
		json.dump(udata, write_data)

def get_user_information():
	if os.path.isfile(USER_INFORMATION_FILE):
		with open(USER_INFORMATION_FILE, "r") as read_user:
			data = json.load(read_user)
			return data
	else:
		# Return default data
		uinfo = {
			"nickname": DEFAULT_NICKNAME,
			"username": DEFAULT_USERNAME,
			"realname": DEFAULT_REALNAME
		}
		return uinfo

CHANNEL_INFO_NAME = 0
CHANNEL_INFO_KEY = 1
CHANNEL_INFO_LIMIT = 2
CHANNEL_INFO_INVITEONLY = 3
CHANNEL_INFO_ALLOWEXTERNAL = 4
CHANNEL_INFO_TOPICLOCKED = 5
CHANNEL_INFO_PROTECTED = 6
CHANNEL_INFO_SECRET = 7
CHANNEL_INFO_MODERATED = 8
CHANNEL_INFO_NOCOLORS = 9