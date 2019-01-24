
from Quirc.Settings import *

import re
import os

def saveColorSettings(qColors,filename):

	colors = {
		"user": qColors.User,
		"self": qColors.Self,
		"action": qColors.Action,
		"notify": qColors.Notify,
		"channel": qColors.Channel,
		"notice": qColors.Notice,
		"normal": qColors.Normal,
		"background": qColors.Background
	}

	with open(filename, "w") as write_data:
		json.dump(colors, write_data)

def loadColorSettings(filename):

	with open(filename, "r") as read_data:
		data = json.load(read_data)

	c = QuircColors()
	c.User = data["user"]
	c.Self = data["self"]
	c.Action = data["action"]
	c.Notify = data["notify"]
	c.Channel = data["channel"]
	c.Notice = data["notice"]
	c.Normal = data["normal"]
	c.Background = data["background"]

	return c

def ColorsInit():
	global GuiColors
	if os.path.isfile(COLOR_FILE):
		GuiColors = loadColorSettings(COLOR_FILE)
	else:
		GuiColors = QuircColors()
		saveColorSettings(GuiColors,COLOR_FILE)

def reloadColors():
	global GuiColors
	GuiColors = loadColorSettings(COLOR_FILE)

def pad_link_nick(nick,size):
	#if len(nick) >= size: return nick
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}<a href=\"{nick}\">{nick}</a>"

def pad_nick(nick,size):
	#if len(nick) >= size: return nick
	x = size - len(nick)
	if x<0 : x = 0
	y = '&nbsp;'*x
	return f"{y}{nick}"

def nolink_chat_message(color,user,txt):
	user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	user = f"<b>{user}</b>"
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	return msg

def chat_message(color,user,txt):
	user = pad_link_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	user = f"<b>{user}</b>"
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	return msg

def chat_icon_message(color,icon,user,txt):
	user = f"<b><a href=\"{user}\">{user}</a></b>"
	msg = CHAT_ICON_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	return msg

def nolink_chat_icon_message(color,icon,user,txt):
	user = f"<b>{user}</b>"
	msg = CHAT_ICON_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	return msg

def notification_message(color,icon,txt):
	msg = MESSAGE_ICON_TEMPLATE.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	return msg

def quirc_msg(txt):
	msg = MESSAGE_ICON_TEMPLATE.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,MSG_QUIRC)
	msg = msg.replace(T_COLOR,GuiColors.Notify)
	return msg

def format_links(txt):
	if COLOR_URL_LINKS:
		LINK_COLOR = URL_LINK_COLOR
	else:
		LINK_COLOR = NORMAL_TEXT_COLOR
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)

	for u in urls:
		link = f"<b><i><a href=\"{u}\"><span style=\"font-style: normal; color: {LINK_COLOR}\">{u}</span></a></i></b>"
		txt = txt.replace(u,link)
	return txt
