
from Quirc.Settings import *
from Quirc.Format import *

def sharedCommands(input,CLIENT,WINDOW,GUI):

	tokens = input.split()

	if len(tokens) >= 1 and tokens[0].lower() == "/join":
		if len(tokens) == 2:
			channel = tokens[1]
			CLIENT.join(channel)
			return True
		if len(tokens) == 3:
			channel = tokens[1]
			key = tokens[2]
			CLIENT.join(channel,key)
			return True
		d = quirc_msg("USAGE: /join CHANNEL [KEY]")
		WINDOW.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/part":
		if len(tokens) == 2:
			channel = tokens[1]
			GUI.partChannel(channel)
			d = quirc_msg(f"Left {channel}")
			GUI.writeToServer(d)
			return True
		d = quirc_msg("USAGE: /part CHANNEL")
		WINDOW.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/quit":
		if len(tokens) >= 2:
			tokens.pop(0)
			msg = " ".join(tokens)
			CLIENT.quit(msg)
			GUI.closeAllWindows()
			return True
		if len(tokens) == 1:
			CLIENT.quit()
			GUI.closeAllWindows()
			return True

	if len(tokens) >= 1 and tokens[0].lower() == "/msg":
		if len(tokens) >= 3:
			tokens.pop(0)
			target = tokens.pop(0)
			msg = " ".join(tokens)
			CLIENT.msg(target,msg,length=MAXIMUM_IRC_MESSAGE_LENGTH)
			channelMsg = False
			if len(target)>1 and target[0] == '#': channelMsg = True
			if len(target)>1 and target[0] == '&': channelMsg = True
			d = chat_message(SELF_NAME_COLOR,CLIENT.nickname,msg)
			if channelMsg:
				if GUI.isInChannel(target): GUI.writeToChannel(target,d)
			else:
				GUI.writeToUser(target,d)
			d = chat_message(SELF_NAME_COLOR,f"{CLIENT.nickname}->{target}",msg)
			GUI.writeToServer(d)
			return True
		d = quirc_msg("USAGE: /msg TARGET MESSAGE")
		WINDOW.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/notice":
		if len(tokens) >= 3:
			tokens.pop(0)
			target = tokens.pop(0)
			msg = " ".join(tokens)
			CLIENT.notice(target,msg)
			channelMsg = False
			if len(target)>1 and target[0] == '#': channelMsg = True
			if len(target)>1 and target[0] == '&': channelMsg = True
			d = chat_icon_message(NOTICE_MESSAGE_COLOR,MSG_CHAT,target,msg)
			if channelMsg:
				if GUI.isInChannel(target): GUI.writeToChannel(target,d)
			else:
				GUI.writeToUser(target,d)
			d = chat_icon_message(NOTICE_MESSAGE_COLOR,MSG_CHAT,f"{CLIENT.nickname}->{target}",msg)
			GUI.writeToServer(d)
			return True
		d = quirc_msg("USAGE: /notice TARGET MESSAGE")
		WINDOW.writeText(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/nick":
		if len(tokens) == 2:
			newnick = tokens[1]
			oldnick = CLIENT.nickname
			CLIENT.QUIRC_setNick(newnick)
			GUI.refreshAllUserLists()
			return True
		d = quirc_msg("USAGE: /nick NEW_NICKNAME")
		WINDOW.writeText(d)
		return True

	return False

def channelHandler(input,CLIENT,WINDOW,GUI):

	# Channel window specific commands
	tokens = input.split()

	if len(tokens) == 1 and tokens[0].lower() == "/part":
		GUI.partChannel(WINDOW.Channel)
		d = quirc_msg(f"Left {WINDOW.Channel}")
		GUI.writeToServer(d)
		return True

	if len(tokens) >= 1 and tokens[0].lower() == "/me":
		if len(tokens) >= 2:
			tokens.pop(0)
			msg = " ".join(tokens)
			CLIENT.msg(WINDOW.Channel,f"\x01ACTION {msg}\x01")
			d = notification_message(ACTION_MESSAGE_COLOR,MSG_USER,f"{CLIENT.nickname} {msg}")
			WINDOW.writeText(d)
			return True
		d = quirc_msg("USAGE: /me MESSAGE")
		WINDOW.writeText(d)
		return True
	
	if sharedCommands(input,CLIENT,WINDOW,GUI):
		return True

	# Command was not handled, return False
	return False

def serverHandler(input,CLIENT,WINDOW,GUI):

	if sharedCommands(input,CLIENT,WINDOW,GUI):
		return True

	# Command was not handled, return False
	return False

def userHandler(input,CLIENT,WINDOW,GUI):

	# User window specific commands
	tokens = input.split()

	if len(tokens) >= 1 and tokens[0].lower() == "/me":
		if len(tokens) >= 2:
			tokens.pop(0)
			msg = " ".join(tokens)
			CLIENT.msg(WINDOW.Nick,f"\x01ACTION {msg}\x01")
			d = notification_message(ACTION_MESSAGE_COLOR,MSG_USER,f"{CLIENT.nickname} {msg}")
			WINDOW.writeText(d)
			return True
		d = quirc_msg("USAGE: /me MESSAGE")
		WINDOW.writeText(d)
		return True
	
	if sharedCommands(input,CLIENT,WINDOW,GUI):
		return True


	# Command was not handled, return False
	return False