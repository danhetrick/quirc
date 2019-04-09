
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
import re
import json

# Globally load in Quirc's resource file
globals()["quirc.resources"] = __import__("quirc.resources")

import quirc.colour

# Globals
APPLICATION_NAME = "Quirc"
APPLICATION_VERSION = "0.22"

DEFAULT_NICKNAME = "quirc"
DEFAULT_USERNAME = "quirc"
DEFAULT_IRCNAME = f"{APPLICATION_NAME} {APPLICATION_VERSION}"

QUIRC_FONT = "Consolas"
QUIRC_FONT_SIZE = 10

QUIRC_HOTKEY_CONNECT = None
QUIRC_HOTKEY_DISCONNECT = "Ctrl+D"
QUIRC_HOTKEY_QUIT = "Ctrl+Q"
QUIRC_HOTKEY_JOIN = "Ctrl+J"
QUIRC_HOTKEY_NICK = "Ctrl+N"
QUIRC_HOTKEY_NETWORK = None

MAXIMUM_IRC_MESSAGE_SIZE = 450

INITIAL_WINDOW_SIZE_WIDTH = 500
INITIAL_WINDOW_SIZE_HEIGHT = 300

LINK_URLS = True

TEXT_BACKGROUND_COLOR = "#ffffff"
TEXT_COLOR = "#000000"
ERROR_COLOR = "#FF0000"
SYSTEM_COLOR = "#FF9C00"
SELF_COLOR = "#FF0000"
USERNAME_COLOR = "#00007F"
ACTION_COLOR = "#009300"
LINK_COLOR = "#00007F"
NOTICE_COLOR = "#9C009C"
MOTD_COLOR = "#00007F"

GRADIENT_LIGHTEN = 0.95

MAX_USERNAME_SIZE = 16

# Paths
INSTALL_DIRECTORY = sys.path[0]
QUIRC_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "quirc")
SETTINGS_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "settings")

IRC_NETWORKS = os.path.join(QUIRC_DIRECTORY, "servers.txt")

LAST_SERVER_INFORMATION_FILE = os.path.join(SETTINGS_DIRECTORY, "lastserver.json")
USER_FILE = os.path.join(SETTINGS_DIRECTORY, "user.json")
COLOR_FILE = os.path.join(SETTINGS_DIRECTORY, "colors.json")

# Graphics
MDI_BACKGROUND = ":/background.png"

QUIRC_ICON = ":/quirc.png"
CHANNEL_ICON = ":/channel.png"
USER_ICON = ":/user.png"
CONNECTED_ICON = ":/connected.png"
DISCONNECTED_ICON = ":/disconnected.png"
SERVER_ICON = ":/server.png"
EXIT_ICON = ":/exit.png"
CASCADE_ICON = ":/cascade.png"
TILE_ICON = ":/tile.png"
NETWORK_ICON = ":/network.png"
HEARTBEAT_ON_ICON = ":/hearton.png"
HEARTBEAT_OFF_ICON = ":/heartoff.png"
ABOUT_ICON = ":/about.png"
FILE_ICON = ":/file.png"
HTML_ICON = ":/html.png"
CLIPBOARD_ICON = ":/clipboard.png"

LOGO_IMAGE = ":/logo.png"
QT_IMAGE = ":/qt.png"
GPL_IMAGE = ":/gpl.png"
PYTHON_IMAGE = ":/python.png"

#Objects

class Whois(object):

	def __init__(self):

		self.name = ''
		self.channels = []
		self.username = ''
		self.host = ''
		self.realname = ''
		self.idle = 0
		self.signedon = ''
		self.server = ''

class Channel(object):

	def __init__(self,name):
		self.name = name
		self.chat = []
		self.users = []
		self.userbuffer = []
		self.window = None
		self.subwindow = None
		self.minimized = False
		self.topic = ""

	def setWindow(self,window):
		self.window = window

	def setSubwindow(self,window):
		self.subwindow = window

	def getWindow(self):
		return self.window

	def getSubwindow(self):
		return self.subwindow

	def channelName(self):
		return self.name

	def addChat(self,user,data):
		c = [user,data]
		self.chat.append(c)

	def channelUsers(self):
		return self.users

	def channelChat(self):
		return self.chat

	def setUsers(self,userlist):
		self.users = userlist

	def addUser(self,user):
		self.userbuffer.append(user)

	def finalizeUsers(self):
		self.users = self.userbuffer
		self.userbuffer = []

# Usefull Functions

def is_integer(n):
	try:
		int(n)
	except ValueError:
		return False
	return True

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

def get_user():
	if os.path.isfile(USER_FILE):
		with open(USER_FILE, "r") as read_user:
			data = json.load(read_user)
			return data
	else:
		si = {
			"nick": DEFAULT_NICKNAME,
			"username": DEFAULT_USERNAME,
			"realname": DEFAULT_IRCNAME
		}
		return si

def save_user(user):
	with open(USER_FILE, "w") as write_data:
		json.dump(user, write_data)

# Text formatting/display

CHAT_TEMPLATE = f"""
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
	  <td style="text-align: left; vertical-align: top; background: \"!BACKGROUND!\";"><font color="!COLOR!"><b>!MESSAGE!</b></font></td>
	</tr>
  </tbody>
</table>
"""

def inject_www_links(txt):
	if not LINK_URLS: return txt
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)
	for u in urls:
		u = re.sub('<[^<]+?>', '', u)
		link = f"<a href=\"{u}\"><span style=\"text-decoration: underline; font-weight: bold; color: {LINK_COLOR}\">{u}</span></a>"
		txt = txt.replace(u,link)
	return txt

def pad_nick(nick,size):
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}{nick}"

def system_display(text):
	msg = SYSTEM_TEMPLATE.replace('!COLOR!',SYSTEM_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	return msg

def error_display(text):
	msg = SYSTEM_TEMPLATE.replace('!COLOR!',ERROR_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	return msg

def chat_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',USERNAME_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(USERNAME_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def mychat_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',SELF_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(SELF_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def action_display(user,text):
	text = remove_html_markup(text)
	text = inject_www_links(text)
	msg = ACTION_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',ACTION_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(ACTION_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def notice_display(user,text,max):
	text = remove_html_markup(text)
	user = pad_nick(user,max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',NOTICE_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(NOTICE_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def motd_display(text,max):
	user = pad_nick("MOTD",max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',MOTD_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(MOTD_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def whois_display(text,max):
	user = pad_nick("WHOIS",max)
	text = inject_www_links(text)
	msg = CHAT_TEMPLATE.replace('!USER!',user)
	msg = msg.replace('!COLOR!',SYSTEM_COLOR)
	msg = msg.replace('!BACKGROUND!',TEXT_BACKGROUND_COLOR)
	msg = msg.replace('!CCHAT!',TEXT_COLOR)
	msg = msg.replace('!MESSAGE!',text)

	# Gradient
	BG = quirc.colour.Color(TEXT_BACKGROUND_COLOR)
	LIGHT_COLOR = quirc.colour.Color(SYSTEM_COLOR,luminance=GRADIENT_LIGHTEN)
	USER_BACKGROUND_GRADIENT = f"background: qlineargradient( x1:0 y1:0, x2:1 y2:0, stop:0 {BG}, stop:1 {LIGHT_COLOR});"
	msg = msg.replace("!GRADIENT!",USER_BACKGROUND_GRADIENT)

	return msg

def makeWhoisPretty(w):
	t = f"""<b>{w.name}</b><br>
<b>Username:</b> {w.username}<br>
<b>Real Name:</b> {w.realname}<br>
<b>Host:</b> {w.host}<br>
<b>Connected to:</b> {w.server}<br>
<b>Signed on:</b> {w.signedon}<br>
<b>Idle:</b> {w.idle} seconds<br>
<b>Channels:</b> {', '.join(w.channels)}"""
	return t


def remove_html_markup(s):
	tag = False
	quote = False
	out = ""

	for c in s:
			if c == '<' and not quote:
				tag = True
			elif c == '>' and not quote:
				tag = False
			elif (c == '"' or c == "'") and tag:
				quote = not quote
			elif not tag:
				out = out + c

	return out

def load_colors():
	if os.path.isfile(COLOR_FILE):
		with open(COLOR_FILE, "r") as read_color:
			data = json.load(read_color)

			global TEXT_BACKGROUND_COLOR
			TEXT_BACKGROUND_COLOR = data["background"]

			global TEXT_COLOR
			TEXT_COLOR = data["text"]

			global ERROR_COLOR
			ERROR_COLOR = data["error"]

			global SYSTEM_COLOR
			SYSTEM_COLOR = data["system"]

			global SELF_COLOR
			SELF_COLOR = data["self"]

			global USERNAME_COLOR
			USERNAME_COLOR = data["username"]

			global ACTION_COLOR
			ACTION_COLOR = data["action"]

			global LINK_COLOR
			LINK_COLOR = data["link"]

			global MOTD_COLOR
			MOTD_COLOR = data["motd"]

			global NOTICE_COLOR
			NOTICE_COLOR = data["notice"]
	else:
		save_colors()

	return [TEXT_BACKGROUND_COLOR,TEXT_COLOR]

def save_colors():
	sinfo = {
			"background": TEXT_BACKGROUND_COLOR,
			"text": TEXT_COLOR,
			"error": ERROR_COLOR,
			"system": SYSTEM_COLOR,
			"self": SELF_COLOR,
			"username": USERNAME_COLOR,
			"action": ACTION_COLOR,
			"link": LINK_COLOR,
			"notice": NOTICE_COLOR,
			"motd": MOTD_COLOR
		}
	with open(COLOR_FILE, "w") as write_data:
		json.dump(sinfo, write_data)
