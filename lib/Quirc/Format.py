
from Quirc.Settings import *

import re

def pad_link_nick(nick,size):
	if len(nick) >= size: return nick
	x = size - len(nick)
	y = '&nbsp;'*x
	return f"{y}<a href=\"{nick}\">{nick}</a>"

def pad_nick(nick,size):
	if len(nick) >= size: return nick
	x = size - len(nick)
	y = '&nbsp;'*x
	return f"{y}{nick}"

def nolink_chat_message(color,user,txt):
	user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	user = f"<b>{user}</b>"
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_NORMAL_COLOR,NORMAL_TEXT_COLOR)
	return msg

def chat_message(color,user,txt):
	user = pad_link_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	user = f"<b>{user}</b>"
	msg = CHAT_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_NORMAL_COLOR,NORMAL_TEXT_COLOR)
	return msg

def chat_icon_message(color,icon,user,txt):
	#user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	#user = f"<b>{user}</b>"
	user = f"<b><a href=\"{user}\">{user}</a></b>"
	msg = CHAT_ICON_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_NORMAL_COLOR,NORMAL_TEXT_COLOR)
	return msg

def nolink_chat_icon_message(color,icon,user,txt):
	#user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
	#user = f"<b>{user}</b>"
	user = f"<b>{user}</b>"
	msg = CHAT_ICON_TEMPLATE.replace(T_USER,user)
	msg = msg.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	msg = msg.replace(T_NORMAL_COLOR,NORMAL_TEXT_COLOR)
	return msg

def notification_message(color,icon,txt):
	msg = MESSAGE_ICON_TEMPLATE.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,icon)
	msg = msg.replace(T_COLOR,color)
	return msg

def quirc_msg(txt):
	msg = MESSAGE_ICON_TEMPLATE.replace(T_MESSAGE,txt)
	msg = msg.replace(T_ICON,MSG_QUIRC)
	msg = msg.replace(T_COLOR,NOTIFICATION_MESSAGE_COLOR)
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
