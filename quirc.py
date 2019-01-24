#
# Quirc IRC Client
#

# Version 0.03001

import sys
import os
import inspect
import random
import json

# local modules
script_filename = inspect.getframeinfo(inspect.currentframe()).filename
script_location = os.path.dirname(os.path.abspath(script_filename))
script_lib = os.path.join(script_location,"lib")
sys.path.append(script_lib)

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

import qt5reactor
qt5reactor.install()

IS_SSL_AVAILABLE = True

from twisted.internet import reactor,protocol

try:
	from twisted.internet import ssl
except ImportError as error:
	IS_SSL_AVAILABLE = False

from twisted.words.protocols import irc

import Quirc.Client.Main as qInterface
from Quirc.Settings import *
from Quirc.Format import *

NICKNAME = "quirc"
REALNAME = "quirc client"
USERNAME = "quirc"

SERVER = 'localhost'
PORT = 6667
SERVER_PASSWORD = ''

class quirc_ClientConnection(irc.IRCClient):

	global GUI
	global NICKNAME
	global REALNAME
	global USERNAME

	nickname = NICKNAME
	realname = REALNAME
	username = USERNAME

	def __init__(self):
		self.CONNECTED = False
		self.Colors = loadColorSettings(COLOR_FILE)
		self.loadSettings()

	def loadSettings(self):
		if os.path.isfile(WINDOW_INFORMATION_FILE):
			with open(WINDOW_INFORMATION_FILE, "r") as read_win:
				data = json.load(read_win)
				self.linkUsers = data["linkUsers"]
				self.linkURL = data["linkURL"]
		else:
			winfo = {
				"initialWidth": 640,
				"initialHeight": 480,
				"linkUsers": True,
				"linkURL": True
			}
			with open(WINDOW_INFORMATION_FILE, "w") as write_data:
				json.dump(winfo, write_data)
			self.linkUsers = True
			self.linkURL = True

	def register(self,nickname,hostname='foo',servername='bar'):
		if SERVER_PASSWORD != '':
			self.sendLine("PASS %s" % SERVER_PASSWORD)
		self.setNick(NICKNAME)
		self.username = USERNAME
		self.realname = REALNAME
		self.sendLine("USER %s %s %s :%s" % (USERNAME, hostname, servername, REALNAME))

	def connectionMade(self):
		GUI.connected(self)
		d = notification_message(self.Colors.Notify,MSG_STAR,f"Connected to {SERVER}:{PORT}")
		#d = notification_message(NOTIFICATION_MESSAGE_COLOR,MSG_STAR,f"Connected to {SERVER}:{PORT}")
		GUI.writeToServer(d)
		GUI.actConnect.setEnabled(False)
		GUI.actDisconnect.setEnabled(True)
		GUI.actDisconnect.setVisible(True)
		GUI.actConnect.setVisible(False)
		return irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):
		d = notification_message(self.Colors.Notify,MSG_STAR,f"Connection to server lost")
		GUI.writeToServer(d)
		self.CONNECTED = False
		GUI.actConnect.setEnabled(True)
		GUI.actDisconnect.setEnabled(False)
		GUI.actDisconnect.setVisible(False)
		GUI.actConnect.setVisible(True)
		return irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		d = notification_message(self.Colors.Notify,MSG_STAR,f"Registered!")
		GUI.writeToServer(d)
		self.CONNECTED = True
		# request full NAMES format
		self.sendLine("PROTOCTL UHNAMES")
		self.join("#quirc")


	def joined(self, channel):
		d = notification_message(self.Colors.Channel,MSG_HASH,f"Joined {channel}")
		GUI.writeToChannel(channel,d)
		self.sendLine(f"NAMES {channel}")

	def privmsg(self, user, target, msg):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]

		# Inject links into chat
		if self.linkURL: msg = format_links(msg)

		if target != self.nickname:
			# public message
			if self.linkUsers:
				d = chat_message(self.Colors.User,pnick,msg)
			else:
				d = nolink_chat_message(self.Colors.User,pnick,msg)
			GUI.writeToChannel(target,d)
			# GUI.writeToChannel(target,f"{pnick}: {msg}")
		else:
			# private message
			d = nolink_chat_message(self.Colors.User,pnick,msg)
			GUI.writeToUser(pnick,d)
			# GUI.writeToUser(pnick,f"{pnick}: {msg}")

	def noticed(self, user, channel, message):
		tokens = user.split('!')
		if len(tokens) >= 2:
			pnick = tokens[0]
			phostmask = tokens[1]
		else:
			pnick = user
			phostmask = user
		d = nolink_chat_icon_message(self.Colors.Notice,MSG_CHAT,pnick,message)
		GUI.writeToActiveWindow(d)
		GUI.writeToServer(d)
		# GUI.writeToActiveWindow(f"NOTICE {pnick}: {message}")
		# GUI.writeToServer(f"NOTICE {pnick}: {message}")

	def receivedMOTD(self, motd):
		for line in motd:
			d = notification_message(self.Colors.Notify,MSG_STAR,line)
			GUI.writeToServer(d)

	def userJoined(self, user, channel):
		d = notification_message(self.Colors.Channel,MSG_HASH,f"{user} joined {channel}")
		GUI.writeToChannel(channel,d)
		self.sendLine(f"NAMES {channel}")

	def userLeft(self, user, channel):
		d = notification_message(self.Colors.Channel,MSG_HASH,f"{user} left {channel}")
		GUI.writeToChannel(channel,d)
		self.sendLine(f"NAMES {channel}")

	def QUIRC_setNick(self,newnick):
		global NICKNAME
		d = quirc_msg(f"Nickname changed from {NICKNAME} to {newnick}")
		NICKNAME = newnick
		self.setNick(NICKNAME)
		self.nickname = newnick
		GUI.writeToActiveWindow(d)
		GUI.writeToServer(d)

	def irc_ERR_NICKNAMEINUSE(self, prefix, params):
		global NICKNAME
		oldNick = self.nickname
		NICKNAME = f"{self.nickname}{random.randint(100, 999)}"
		self.setNick(NICKNAME)
		d = notification_message(self.Colors.Notify,MSG_STAR,f"Nickname {oldNick} taken! Trying to use {NICKNAME} as new nickname...")
		GUI.writeToActiveWindow(d)
		GUI.writeToServer(d)

	def userRenamed(self, oldname, newname):
		d = notification_message(self.Colors.Channel,MSG_HASH,f"{oldname} is now known as {newname}")
		GUI.writeToActiveWindow(d)
		GUI.writeToServer(d)

	def topicUpdated(self, user, channel, newTopic):
		if newTopic == "": return
		d = notification_message(self.Colors.Channel,MSG_HASH,f"{user} set {channel}'s topic to \"{newTopic}\"")
		GUI.writeToChannel(channel,d)
		GUI.channelTopic(channel,newTopic)

	def irc_RPL_TOPIC(self, prefix, params):
		channel = params[1]
		if not params[2].isspace():
			if params[2] != '':
				d = notification_message(self.Colors.Channel,MSG_HASH,f"{channel}'s topic is \"{params[2]}\"")
				GUI.writeToChannel(channel,d)
			GUI.channelTopic(channel,params[2])
		else:
			GUI.channelTopic(channel,'')

	def action(self, user, channel, data):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]
		if channel == self.nickname:
			# private
			d = notification_message(self.Colors.Action,MSG_USER,f"{pnick} {data}")
			GUI.writeToUser(pnick,d)
		else:
			#public
			d = notification_message(self.Colors.Action,MSG_USER,f"{pnick} {data}")
			GUI.writeToChannel(channel,d)

	def userKicked(self, kickee, channel, kicker, message):
		if len(message)>0:
			d = notification_message(self.Colors.Channel,MSG_HASH,f"{kicker} kicked {kickee} from {channel} ({message})")
			GUI.writeToChannel(channel,d)
		else:
			d = notification_message(self.Colors.Channel,MSG_HASH,f"{kicker} kicked {kickee} from {channel}")
			GUI.writeToChannel(channel,d)
		self.sendLine(f"NAMES {channel}")

	def kickedFrom(self, channel, kicker, message):
		if len(message)>0:
			pass
		else:
			pass

	def irc_QUIT(self,prefix,params):
		x = prefix.split('!')
		if len(x) >= 2:
			nick = x[0]
			hostmask = x[1]
		else:
			nick = prefix
			hostmask = prefix
		if len(params) >=1:
			m = params[0].split(':')
			if len(m)>=2:
				msg = m[1].strip()
				d = notification_message(self.Colors.Channel,MSG_HASH,f"{nick} quit IRC ({msg})")
			else:
				d = notification_message(self.Colors.Channel,MSG_HASH,f"{nick} quit IRC")
			GUI.writeToActiveWindow(d)
			GUI.writeToServer(d)

	def modeChanged(self, user, channel, set, modes, args):
		channelUserChange = False
		if "o" in modes: channelUserChange = True
		if "v" in modes: channelUserChange = True
		if channelUserChange: self.sendLine(f"NAMES {channel}")
		p = user.split('!')
		if len(p) == 2:
			pnick = user.split('!')[0]
			phostmask = user.split('!')[1]
		else:
			pnick = user
			phostmask = user

	def irc_RPL_NAMREPLY(self, prefix, params):
		channel = params[2].lower()
		nicklist = params[3].split(' ')
		GUI.addUsersToChannel(channel,nicklist)

	def irc_RPL_ENDOFNAMES(self, prefix, params):
		channel = params[1]
		GUI.endOfUserList(channel)

	def lineReceived(self, line):
		try:
			line2 = line.decode('UTF-8')
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		d = line2.split(" ")
		if len(d) >= 2:
			if d[1].isalpha(): return irc.IRCClient.lineReceived(self, line)
		errMsg = ''
		if "Cannot join channel (+k)" in line2:
			errMsg = quirc_msg("Cannot join channel (wrong or missing password)")
		if "Cannot join channel (+l)" in line2:
			errMsg = quirc_msg("Cannot join channel (channel is full)")
		if "Cannot join channel (+b)" in line2:
			errMsg = quirc_msg("Cannot join channel (banned)")
		if "Cannot join channel (+i)" in line2:
			errMsg = quirc_msg("Cannot join channel (channel is invite only)")
		if "not an IRC operator" in line2:
			errMsg = quirc_msg("Permission denied (you're not an IRC operator")
		if "not channel operator" in line2:
			errMsg = quirc_msg("Permission denied (you're not channel operator)")
		if "is already on channel" in line2:
			errMsg = quirc_msg("Invite failed (user is already in channel)")
		if "not on that channel" in line2:
			errMsg = quirc_msg("Permission denied (you're not in channel)")
		if "aren't on that channel" in line2:
			errMsg = quirc_msg("Permission denied (target user is not in channel)")
		if "have not registered" in line2:
			errMsg = quirc_msg("You're not registered")
		if "may not reregister" in line2:
			errMsg = quirc_msg("You can't reregister")
		if "enough parameters" in line2:
			errMsg = quirc_msg("Error: not enough parameters supplied to command")
		if "isn't among the privileged" in line2:
			errMsg = quirc_msg("Registration refused (server isn't setup to allow connections from your host)")
		if "Password incorrect" in line2:
			errMsg = quirc_msg("Permission denied (incorrect password)")
		if "banned from this server" in line2:
			errMsg = quirc_msg("You are banned from this server")
		if "kill a server" in line2:
			errMsg = quirc_msg("Permission denied (you can't kill a server)")
		if "O-lines for your host" in line2:
			errMsg = quirc_msg("Error: no O-lines for your host")
		if "Unknown MODE flag" in line2:
			errMsg = quirc_msg("Error: unknown MODE flag")
		if "change mode for other users" in line2:
			errMsg = quirc_msg("Permission denied (can't change mode for other users)")
		if len(errMsg)>0:
			GUI.writeToActiveWindow(errMsg)
			GUI.writeToServer(errMsg)
		return irc.IRCClient.lineReceived(self, line)


class quirc_ConnectionFactory(protocol.ClientFactory):
	def __init__(self):
		self.config = 0

	def buildProtocol(self, addr):
		global CLIENT
		CLIENT = quirc_ClientConnection()
		CLIENT.factory = self

		with open(USER_INFORMATION_FILE, "r") as read_user:
				data = json.load(read_user)
		CLIENT.nickname = data["nickname"]
		CLIENT.username = data["username"]
		CLIENT.realname = data["realname"]

		return CLIENT

	def clientConnectionLost(self, connector, reason):
		pass

	def clientConnectionFailed(self, connector, reason):
		pass

def tcp_to_irc(host,port):
	global CLIENT
	global SERVER
	global PORT
	global GUI
	SERVER = host
	PORT = int(port)

	GUI.connecting(host)
	CLIENT = quirc_ConnectionFactory()
	reactor.connectTCP(host, int(port), CLIENT)
	return CLIENT

def ssl_to_irc(host,port):
	global CLIENT
	global SERVER
	global PORT
	global GUI
	SERVER = host
	PORT = int(port)

	GUI.connecting(host)
	CLIENT = quirc_ConnectionFactory()
	reactor.connectSSL(host, int(port), CLIENT, ssl.ClientContextFactory())
	return CLIENT

def restart_program():
	"""Restarts the current program.
	Note: this function does not return. Any cleanup action (like
	saving data) must be done before calling this function."""
	python = sys.executable
	os.execl(python, python, * sys.argv)

if __name__ == '__main__':
	global GUI

	ColorsInit()

	# Load user info file if present...
	if os.path.isfile(USER_INFORMATION_FILE):
		with open(USER_INFORMATION_FILE, "r") as read_user:
			data = json.load(read_user)
			NICKNAME = data["nickname"]
			USERNAME = data["username"]
			REALNAME = data["realname"]
	else:
		# ...and generate it if not
		uinfo = {
			"nickname": NICKNAME,
			"username": USERNAME,
			"realname": REALNAME
		}
		with open(USER_INFORMATION_FILE, "w") as write_data:
			json.dump(uinfo, write_data)

	GUI = qInterface.Window(tcp_to_irc,ssl_to_irc,IS_SSL_AVAILABLE,restart_program)
	GUI.show()

	reactor.run()