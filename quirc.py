# ============
# | quirc.py |
# ============
#
#  ██████╗ ██╗   ██╗██╗██████╗  ██████╗
# ██╔═══██╗██║   ██║██║██╔══██╗██╔════╝
# ██║   ██║██║   ██║██║██████╔╝██║     
# ██║▄▄ ██║██║   ██║██║██╔══██╗██║     
# ╚██████╔╝╚██████╔╝██║██║  ██║╚██████╗
#  ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝
# A Python/Qt5 IRC client
#

# ===========================
# | APPLICATION INFORMATION |
# ===========================

APPLICATION = "Quirc"
VERSION = "0.01643"
DESCRIPTION = "A Python3/Qt5 IRC client"

# ========================
# | IRC NETWORK SETTINGS |
# ========================

SERVER = "none"
PORT = 0
CHANNEL = "#quirc"
CHANNEL_PASSWORD = ""
DEFAULT_CHANNEL = "#quirc"

NICKNAME = "quirc"
REALNAME = f"{APPLICATION} IRC Client v{VERSION}"
USERNAME = "quirc"

# =======================
# | IRC CLIENT SETTINGS |
# =======================

CLIENT_FONT = "Courier New"

RUN_IN_GADGET_MODE = False
GADGET_X = 0
GADGET_Y = 0
GADGET_WIDTH = 600
GADGET_HEIGHT = 600
GADGET_ALWAYS_ON_TOP = False

IRC_SSL = True

WINDOW_TITLE = "Disconnected"

HIGH_CONTRAST = False

CREATE_LINKS = True

MAXIMUM_IRC_MESSAGE_LENGTH = 450

STARTUP_SCRIPT = ''

SCRIPT_VARIABLES = []

# ================================
# | HANDLE COMMANDLINE ARGUMENTS |
# ================================

import argparse
parser = argparse.ArgumentParser(prog=f"python quirc.py", description=f"{APPLICATION} {VERSION} - {DESCRIPTION}")

parser.add_argument("-g","--gadget", help="Run Quirc as a screen gadget", action='store_true')
parser.add_argument("-x", help="Gadget's X location (default: 0)", type=int)
parser.add_argument("-y", help="Gadget's Y location (default: 0)", type=int)
parser.add_argument("-w","--width", help="Gadget's width  (default: 600)", type=int)
parser.add_argument("-H","--height", help="Gadget's height (default: 600)", type=int)
parser.add_argument("-t","--ontop", help="Gadget will always be on top", action='store_true')

parser.add_argument("-c","--channel", help="IRC channel to join")
parser.add_argument("-p","--password", help="IRC channel password to use")
parser.add_argument("-n","--nick", help="Nickname to use (default: quirc)")
parser.add_argument("-u","--username", help="Username to use (default: quirc)")
parser.add_argument("-d","--default", help="Set default channel (default: #quirc)")

parser.add_argument("-f","--font", help="Set display font (default: Courier New)")
parser.add_argument("-C","--highcontrast", help="Run Quirc in high contrast mode", action='store_true')

parser.add_argument("-l","--nolinks", help="Don't change URLs in chat to links", action='store_true')

parser.add_argument("-m","--maxlength", help="Maximum character length of IRC messages sent  (default: 450)", type=int)

parser.add_argument("-s","--script", help="Script to run on startup")

args = parser.parse_args()

if args.nick:
	NICKNAME = args.nick
if args.username:
	USERNAME = args.username
if args.channel:
	CHANNEL = args.channel
if args.password:
	CHANNEL_PASSWORD = args.password
if args.default:
	DEFAULT_CHANNEL = args.default

if args.font:
	CLIENT_FONT = args.font

if args.nolinks:
	CREATE_LINKS = False

if args.highcontrast:
	HIGH_CONTRAST = True

if args.maxlength:
	MAXIMUM_IRC_MESSAGE_LENGTH = args.maxlength

if args.script:
	STARTUP_SCRIPT = args.script

if args.gadget:
	RUN_IN_GADGET_MODE = True
	if args.x:
		GADGET_X = args.x
	if args.y:
		GADGET_Y = args.y
	if args.width:
		GADGET_WIDTH = args.width
	if args.height:
		GADGET_HEIGHT = args.height
	if args.ontop:
		GADGET_ALWAYS_ON_TOP = True

# ===================
# | LIBRARY IMPORTS |
# ===================

import sys
import random
from datetime import datetime, timedelta
import re
import time

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

import qt5reactor
qt5reactor.install()
from twisted.internet import reactor, protocol

try:
	from twisted.internet import ssl
except ImportError as error:
	# Output expected ImportErrors.
	print(error.__class__.__name__ + ": " + error.message)
	IRC_SSL = False
except Exception as exception:
	# Output unexpected Exceptions.
	print(exception, False)
	print(exception.__class__.__name__ + ": " + exception.message)

from twisted.words.protocols import irc

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

# ==============================
# | WIDGET SIZES AND LOCATIONS |
# ==============================

input_height = 22
output_width = 440
output_height = 400
text_x = 10
user_width = 150
user_height = 400
user_x = text_x + output_width + 10
input_width = output_width + user_width + 10

text_y = 40
output_y = 5

window_width = output_width + user_width + text_y
window_height = output_height + input_height + text_y

# =====================
# | RUN TIME SETTINGS |
# =====================

CHANNEL_USER_LIST = []
CONNECTED = False

PUBLIC_MESSAGE_COLOR = "blue"
PRIVATE_MESSAGE_COLOR = "magenta"
SYSTEM_MESSAGE_COLOR = "grey"
CTCP_ACTION_MESSAGE_COLOR = "green"
NOTICE_MESSAGE_COLOR = "purple"
WHOIS_MESSAGE_COLOR = "orange"
ERROR_MESSAGE_COLOR = "red"

if HIGH_CONTRAST:
	PUBLIC_MESSAGE_COLOR = "aqua"
	SYSTEM_MESSAGE_COLOR = "silver"
	NOTICE_MESSAGE_COLOR = "fuchsia"
	CTCP_ACTION_MESSAGE_COLOR = "lime"

PUBLIC_MESSAGE_SYMBOL = f"<font color=\"{PUBLIC_MESSAGE_COLOR}\">&#9679;</font> "
SYSTEM_MESSAGE_SYMBOL = f"<font color=\"{SYSTEM_MESSAGE_COLOR}\">&#9679;</font> "
PRIVATE_MESSAGE_SYMBOL = f"<font color=\"{PRIVATE_MESSAGE_COLOR}\">&#9679;</font> "
NOTICE_MESSAGE_SYMBOL = f"<font color=\"{NOTICE_MESSAGE_COLOR}\">&#9679;</font> "
WHOIS_MESSAGE_SYMBOL = f"<font color=\"{WHOIS_MESSAGE_COLOR}\">&#9679;</font> "
ERROR_MESSAGE_SYMBOL = f"<font color=\"{ERROR_MESSAGE_COLOR}\">&#9679;</font> "

CLIENT_IS_OPERATOR = False
CLIENT_IS_AWAY = False
NO_TOPIC = " "
TOPIC = NO_TOPIC
CHANNEL_KEY = CHANNEL_PASSWORD

LOGO = """ ██████╗ ██╗   ██╗██╗██████╗  ██████╗
██╔═══██╗██║   ██║██║██╔══██╗██╔════╝
██║   ██║██║   ██║██║██████╔╝██║     
██║▄▄ ██║██║   ██║██║██╔══██╗██║     
╚██████╔╝╚██████╔╝██║██║  ██║╚██████╗
 ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝"""

SCRIPT_COMMENT_SYMBOL = ';'

UPTIME = 0

# ============================
# | GRAPHICAL USER INTERFACE |
# ============================

class UptimeThread(QThread):

	def __init__(self):
		QThread.__init__(self)

	def run(self):
		global UPTIME
		while 1:
			time.sleep(1)
			UPTIME = UPTIME + 1

class DelayThread(QThread):
	signal = pyqtSignal('PyQt_PyObject')

	def __init__(self):
		QThread.__init__(self)
		self.code = ''
		self.time = 0

	def run(self):
		global UPTIME
		thingy = [self, self.code]
		while 1:
			if UPTIME >= self.time:
				self.signal.emit(thingy)
				break

class Quirc_IRC_Client(QWidget):

	def __init__(self):
		super().__init__()
		self.createQuircUI()
		# Start uptime thread
		self.uthread = UptimeThread()
		self.uthread.start()
		self.delayed_scripts = []

	#def keyPressEvent(self,event):
		#if event.key() == Qt.Key_Up:
			#print("Got key up!")
		#if event.key() == Qt.Key_Down:
			#print("Got key down!")

	def delay_script(self,t,text):
		dthread = DelayThread()
		dthread.code = text
		dthread.time = UPTIME + t
		dthread.signal.connect(self.delayed)
		dthread.start()
		self.delayed_scripts.append(dthread)

	def delayed(self,thingy):
		obj = thingy[0]
		code = thingy[1]
		handle_commands(self,code)
		del obj

	# Handle window resizing
	def resizeEvent(self,resizeEvent):
		rwindow_width = self.width()
		rwindow_height = self.height()
		display_height = rwindow_height -70
		topic_and_channel_y = text_y-25
		self.user_list.setGeometry(QtCore.QRect(rwindow_width-user_width-10, text_y, user_width, display_height))
		self.channel.setGeometry(QtCore.QRect(rwindow_width-user_width-10, topic_and_channel_y, user_width, self.channel.height()))
		self.chat_display.setGeometry(QtCore.QRect(text_x, text_y, rwindow_width-self.user_list.width()-22, display_height))
		self.topic.setGeometry(QtCore.QRect(text_x, topic_and_channel_y, rwindow_width-self.user_list.width()-25, self.topic.height()))
		self.irc_input.setGeometry(QtCore.QRect(text_x, text_y+self.chat_display.height()+2, rwindow_width-20, input_height))

		self.server.setGeometry(QtCore.QRect(text_x, -5, output_width+user_width+5, self.channel.height()))

	def user_input(self):
		txt = self.irc_input.text()
		self.irc_input.setText('')
		handle_user_input(self,txt)

	def closeEvent(self, event):
		app.quit()

	def changeTitle(self,text):
		self.setWindowTitle(text)

	def createQuircUI(self):

		self.setWindowTitle(f"{APPLICATION} {VERSION}")

		font = QFont(CLIENT_FONT, 10)
		channel_and_topic_font = QFont(CLIENT_FONT, 10, QFont.Bold)
		userfont = QFont(CLIENT_FONT, 10, QFont.Bold)

		# Channel name display
		self.server = QLabel(self)
		self.server.setText(" ")
		self.server.move(text_x,0)
		self.server.setFont(channel_and_topic_font)
		self.server.setGeometry(QtCore.QRect(self.server.x(), self.server.y(), output_width+user_width, self.server.height()))
		self.server.installEventFilter(self)

		# Channel name display
		self.channel = QLabel(self)
		self.channel.setText(" ")
		self.channel.move(user_x,0)
		self.channel.setFont(channel_and_topic_font)
		self.channel.setGeometry(QtCore.QRect(self.channel.x(), self.channel.y(), user_width, self.channel.height()))
		self.channel.installEventFilter(self)

		# Channel topic display
		self.topic = QLabel(self)
		self.topic.setText(f"{TOPIC}")
		self.topic.move(text_x,0)
		self.topic.setFont(channel_and_topic_font)
		self.topic.setGeometry(QtCore.QRect(self.topic.x(), self.topic.y(), output_width, self.topic.height()))
		self.topic.installEventFilter(self)
		
		# User input
		self.irc_input = QLineEdit(self)
		self.irc_input.setGeometry(QtCore.QRect(text_x, input_height+output_height+10, input_width, input_height))
		self.irc_input.setObjectName("irc_input")
		self.irc_input.returnPressed.connect(self.user_input)
		self.irc_input.setFont(font)
		
		# Chat display
		self.chat_display = QTextBrowser(self)
		self.chat_display.setGeometry(QtCore.QRect(text_x, text_y, output_width, output_height))
		self.chat_display.setObjectName("chat_display")
		self.chat_display.setFont(font)

		write_to_display(self,f"{LOGO}")
		write_to_display(self,f"<b>Version {VERSION}</b>")
		write_to_display(self,f"<b><i>{DESCRIPTION}</i></b>")
		write_to_display(self,"")
		write_to_display(self,"Enter a command to connect to IRC!")
		display_help(self)

		if CREATE_LINKS:
			self.chat_display.setOpenExternalLinks(True)
			
		# Channel user list
		self.user_list = QListWidget(self)
		self.user_list.setGeometry(QtCore.QRect(user_x, text_y, user_width, user_height))
		self.user_list.setObjectName("user_list")
		self.user_list.setFont(userfont)
		self.user_list.installEventFilter(self)

		self.irc_input.setText("/connect localhost 6667")

		if HIGH_CONTRAST:
			self.chat_display.setStyleSheet("QTextBrowser { background-color: #000000; color: white }")
			self.user_list.setStyleSheet("QListWidget { background-color: #000000; color: white }")
			self.irc_input.setStyleSheet("QLineEdit { background-color: #000000; color: white }")
			self.setStyleSheet("QWidget { background-color: #000000; color: white }")
			self.channel.setStyleSheet("QLabel { background-color: #000000; color: white }")
			self.topic.setStyleSheet("QLabel { background-color: #000000; color: white }")
			self.server.setStyleSheet("QLabel { background-color: #000000; color: white }")

		if RUN_IN_GADGET_MODE:
			if GADGET_ALWAYS_ON_TOP:
				self.setWindowFlags(
					QtCore.Qt.FramelessWindowHint |
					QtCore.Qt.WindowStaysOnTopHint |
					QtCore.Qt.Tool
					)
			else:
				self.setWindowFlags(
					QtCore.Qt.FramelessWindowHint |
					QtCore.Qt.Tool
					)

			self.setGeometry(QtCore.QRect(GADGET_X, GADGET_Y, GADGET_WIDTH, GADGET_HEIGHT))
		else:
			self.setGeometry(QtCore.QRect(100, 100, self.chat_display.width()+self.user_list.width()+25, self.chat_display.height()+self.channel.height()+self.irc_input.height()))

		self.show()

	# GUI right-click context menus
	def eventFilter(self, source, event):
		global CHANNEL
		global bot
		global CLIENT_IS_OPERATOR

		if (event.type() == QtCore.QEvent.ContextMenu and
				source is self.channel):

			if CLIENT_IS_OPERATOR:
				menu = QMenu()
				addKey = menu.addAction('Set channel key')
				removeKey = menu.addAction('Remove channel key')
				menu.addSeparator()
				chanPriv = menu.addAction('Make channel private')
				chanPub = menu.addAction('Make channel public')
				menu.addSeparator()
				chanMod = menu.addAction('Make channel moderated')
				chanNoMod = menu.addAction('Make channel unmoderated')
				menu.addSeparator()
				onlyLocal = menu.addAction('Block non-local messages')
				notOnlyLocal = menu.addAction('Unblock non-local messages')
				action = menu.exec_(self.channel.mapToGlobal(event.pos()))

				if action == addKey:
					self.irc_input.setText("/key ")
					self.irc_input.setFocus()
					return True

				if action == removeKey:
					bot.mode(CHANNEL,False,"k",user=f"{CHANNEL_KEY}")
					system_msg_display(self,"Channel key removed")
					return True

				if action == chanPriv:
					bot.mode(CHANNEL,True,"p")
					system_msg_display(self,"Channel set to private")
					return True

				if action == chanPub:
					bot.mode(CHANNEL,False,"p")
					system_msg_display(self,"Channel set to public")
					return True

				if action == chanMod:
					bot.mode(CHANNEL,True,"m")
					system_msg_display(self,"Channel set to moderated")
					return True

				if action == chanNoMod:
					bot.mode(CHANNEL,False,"m")
					system_msg_display(self,"Channel set to unmoderated")
					return True

				if action == onlyLocal:
					bot.mode(CHANNEL,True,"n")
					system_msg_display(self,"Channel set to block non-local messages")
					return True

				if action == notOnlyLocal:
					bot.mode(CHANNEL,False,"n")
					system_msg_display(self,"Channel set to unblock non-local messages")
					return True

		if (event.type() == QtCore.QEvent.ContextMenu and
				source is self.server):
			if not CONNECTED: return True

			menu = QMenu()
			copyServer = menu.addAction('Copy server to clipboard')
			copyServer2 = menu.addAction('Copy server URL to clipboard')
			action = menu.exec_(self.server.mapToGlobal(event.pos()))

			if action == copyServer:
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText(f"{SERVER}:{PORT}", mode=cb.Clipboard)
				return True

			if action == copyServer2:
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText(f"irc://{SERVER}:{PORT}", mode=cb.Clipboard)
				return True

		if (event.type() == QtCore.QEvent.ContextMenu and
				source is self.topic):

			if not CONNECTED: return True

			if CLIENT_IS_OPERATOR:
				menu = QMenu()
				setTopic = menu.addAction('Set Topic')
				copyTopic = menu.addAction('Copy topic to clipboard')
				action = menu.exec_(self.topic.mapToGlobal(event.pos()))

				if action == setTopic:
						self.irc_input.setText("/topic ")
						self.irc_input.setFocus()
						return True

				if action == copyTopic:
						cb = QApplication.clipboard()
						cb.clear(mode=cb.Clipboard )
						cb.setText(TOPIC, mode=cb.Clipboard)
						return True
			else:
				menu = QMenu()
				copyTopic = menu.addAction('Copy topic to clipboard')
				action = menu.exec_(self.topic.mapToGlobal(event.pos()))

				if action == copyTopic:
						cb = QApplication.clipboard()
						cb.clear(mode=cb.Clipboard )
						cb.setText(TOPIC, mode=cb.Clipboard)
						return True

		if CLIENT_IS_OPERATOR:
			if (event.type() == QtCore.QEvent.ContextMenu and
				source is self.user_list):

				item = source.itemAt(event.pos())
				if item is None: return True

				menu = QMenu()
				opAct = menu.addAction('Give ops')
				unopAct = menu.addAction('Take ops')
				voAct = menu.addAction('Give voice')
				unvoAct = menu.addAction('Take voice')
				kickAct = menu.addAction('Kick user')
				menu.addSeparator()
				msgAct = menu.addAction('Send message')
				noticeAct = menu.addAction('Send notice')
				menu.addSeparator()
				whoisAct = menu.addAction('WHOIS user')
				whoisCAct = menu.addAction('WHOIS channel')
				menu.addSeparator()
				copyAct = menu.addAction('Copy users to clipboard')
				action = menu.exec_(self.user_list.mapToGlobal(event.pos()))

				target = item.text()
				target = target.replace("@","")
				target = target.replace("+","")

				if action == kickAct:
					bot.kick(CHANNEL,target)
					fetch_userlist(bot)
					return True

				if action == unopAct:
					bot.mode(CHANNEL,False,"o",user=target)
					return True

				if action == voAct:
					bot.mode(CHANNEL,True,"v",user=target)
					return True

				if action == unvoAct:
					bot.mode(CHANNEL,False,"v",user=target)
					return True

				if action == msgAct:
					self.irc_input.setText(f"/msg {target} ")
					self.irc_input.setFocus()
					return True

				if action == opAct:
					bot.mode(CHANNEL,True,"o",user=target)
					return True

				if action == noticeAct:
					self.irc_input.setText(f"/notice {target} ")
					self.irc_input.setFocus()
					return True

				if action == whoisAct:
					bot.whois(target)
					system_msg_display(self,f"Requested WHOIS data for {target}")
					return True

				if action == whoisCAct:
					bot.whois(CHANNEL)
					system_msg_display(self,f"Requested WHOIS data for {CHANNEL}")
					return True

				if action == copyAct:
					ulist = get_userlist(self)
					cb = QApplication.clipboard()
					cb.clear(mode=cb.Clipboard )
					cb.setText(' '.join(ulist), mode=cb.Clipboard)
					return True
		else:
			if (event.type() == QtCore.QEvent.ContextMenu and
				source is self.user_list):

				item = source.itemAt(event.pos())
				if item is None: return True

				menu = QMenu()
				msgAct = menu.addAction('Send message')
				noticeAct = menu.addAction('Send notice')
				menu.addSeparator()
				whoisAct = menu.addAction('WHOIS user')
				whoisCAct = menu.addAction('WHOIS channel')
				menu.addSeparator()
				copyAct = menu.addAction('Copy users to clipboard')
				action = menu.exec_(self.user_list.mapToGlobal(event.pos()))

				target = item.text()
				target = target.replace("@","")
				target = target.replace("+","")

				if action == whoisAct:
					bot.whois(target)
					system_msg_display(self,f"Requested WHOIS data for {target}")
					return True

				if action == whoisCAct:
					bot.whois(CHANNEL)
					system_msg_display(self,f"Requested WHOIS data for {CHANNEL}")
					return True

				if action == msgAct:
					self.irc_input.setText(f"/msg {target} ")
					self.irc_input.setFocus()
					return True

				if action == noticeAct:
					self.irc_input.setText(f"/notice {target} ")
					self.irc_input.setFocus()
					return True

				if action == copyAct:
					ulist = get_userlist(self)
					cb = QApplication.clipboard()
					cb.clear(mode=cb.Clipboard )
					cb.setText(' '.join(ulist), mode=cb.Clipboard)
					return True

		return super(Quirc_IRC_Client, self).eventFilter(source, event)

# =====================================
# | TWISTED IRC CONNECTION MANAGEMENT |
# =====================================

class QuircClientConnection(irc.IRCClient):
	nickname = NICKNAME
	realname = REALNAME
	username = USERNAME

	def __init__(self):
		self.beep = 1

	def connectionMade(self):
		global CONNECTED
		CONNECTED = True
		irc.IRCClient.connectionMade(self)
		ircform.server.setText(f"Connecting to {SERVER}:{PORT}")
		system_msg_display(ircform,f"Connecting to {SERVER}:{PORT}")

	def connectionLost(self, reason):
		global CONNECTED
		CONNECTED = False
		system_msg_display(ircform,"Connection lost.")
		update_server_label(ircform)
		empty_userlist(ircform)
		ircform.channel.setText("")
		irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		system_msg_display(ircform,"Connected!")
		update_server_label(ircform)
		self.join(CHANNEL, CHANNEL_PASSWORD)

	def joined(self, channel):
		ircform.channel.setText(f"{channel}")
		fetch_userlist(self)
		system_msg_display(ircform,f"Joined {channel}")

	def privmsg(self, user, target, msg):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]

		if target != self.nickname:
			chat_msg_display(ircform,pnick,msg)
		else:
			private_msg_display(ircform,pnick,msg)

	def noticed(self, user, channel, message):
		tok = user.split('!')
		if len(tok) >= 2:
			pnick = tok[0]
			phostmask = tok[1]
		else:
			pnick = user
			phostmask = user
		notice_msg_display(ircform,pnick,message)

	def receivedMOTD(self, motd):
		for line in motd:
			system_msg_display(ircform,f"{line}")

	def modeChanged(self, user, channel, set, modes, args):
		p = user.split('!')
		if len(p) == 2:
			pnick = user.split('!')[0]
			phostmask = user.split('!')[1]
		else:
			pnick = user
			phostmask = user
		if 'o' in modes:
			if set:
				for u in args:
					system_msg_display(ircform,f"{pnick} gave {u} operator status")
					fetch_userlist(self)
			else:
				for u in args:
					system_msg_display(ircform,f"{pnick} took operator status from {u}")
					fetch_userlist(self)
		if 'v' in modes:
			if set:
				for u in args:
					system_msg_display(ircform,f"{pnick} gave {u} voiced status")
					fetch_userlist(self)
			else:
				for u in args:
					system_msg_display(ircform,f"{pnick} took voiced status from {u}")
					fetch_userlist(self)
		if 'p' in modes:
			if set:
				system_msg_display(ircform,f"{pnick} set channel status to private")
			else:
				system_msg_display(ircform,f"{pnick} set channel status to public")
		if 'k' in modes:
			if len(args) >= 1:
				nkey = args[0]
			else:
				nkey = ''
			if set:
				system_msg_display(ircform,f"{pnick} set channel key to '{nkey}'")
			else:
				system_msg_display(ircform,f"{pnick} removed channel key")
		if channel == NICKNAME:
			for m in modes:
				if set:
					system_msg_display(ircform,f"Client mode +{m} set")
				else:
					system_msg_display(ircform,f"Client mode -{m} set")
		

	def userQuit(self, user, quitMessage):
		system_msg_display(ircform,f"{user} quit IRC {quitMessage}")
		fetch_userlist(self)

	def userJoined(self, user, channel):
		system_msg_display(ircform,f"{user} joined {channel}")
		fetch_userlist(self)

	def userLeft(self, user, channel):
		system_msg_display(ircform,f"{user} left {channel}")
		fetch_userlist(self)

	def irc_ERR_NICKNAMEINUSE(self, prefix, params):
		global NICKNAME
		NICKNAME = f"{NICKNAME}{random.randint(100, 999)}"
		self.setNick(NICKNAME)
		update_server_label(ircform)

	def userRenamed(self, oldname, newname):
		system_msg_display(ircform,f"User {oldname} changed their nick to {newname}")
		fetch_userlist(self)

	def topicUpdated(self, user, channel, newTopic):
		global TOPIC
		system_msg_display(ircform,f"User {user} set topic on {channel} to '{newTopic}'")
		if newTopic == "" or newTopic.isspace():
			TOPIC = NO_TOPIC
			ircform.topic.setText(f"{TOPIC}")
			return
		TOPIC = newTopic
		ircform.topic.setText(f"{TOPIC}")

	def action(self, user, channel, data):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]
		action_msg_display(ircform,pnick,data)

	def userKicked(self, kickee, channel, kicker, message):
		system_msg_display(ircform,f"{kicker} kicked {kickee} from {channel} ({message})")

	def kickedFrom(self, channel, kicker, message):
		system_msg_display(ircform,f"Kicked from {channel} by {kicker} ({message})")
		self.join(DEFAULT_CHANNEL)

	def irc_RPL_NAMREPLY(self, prefix, params):
		channel = params[2].lower()
		nicklist = params[3].split(' ')
		for nick in nicklist:
			CHANNEL_USER_LIST.append(nick)

	def irc_RPL_ENDOFNAMES(self, prefix, params):
		ulist = sort_nicks(CHANNEL_USER_LIST)
		empty_userlist(ircform)
		for nick in ulist:
			add_to_user_list(ircform,nick)


	def irc_RPL_TOPIC(self, prefix, params):
		global TOPIC
		if not params[2].isspace():
			TOPIC = params[2]
			ircform.topic.setText(f"{TOPIC}")
		else:
			TOPIC = NO_TOPIC
			ircform.topic.setText(f"{TOPIC}")

	def irc_RPL_WHOISCHANNELS(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		channels = ", ".join(params)
		whois_msg_display(ircform,f"{nick} is in {channels}")

	def irc_RPL_WHOISUSER(self, prefix, params):
		nick = params[1]
		username = params[2]
		host = params[3]
		realname = params[5]
		whois_msg_display(ircform,f"{nick}({username})'s host is {host}")

	def irc_RPL_WHOISIDLE(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		idle_time = params.pop(0)
		signed_on = params.pop(0)

		idle_time = pretty_time(idle_time)
		signed_on = datetime.fromtimestamp(int(signed_on)).strftime("%A, %B %d, %Y %I:%M:%S")
		whois_msg_display(ircform,f"{nick} connected on {signed_on}")
		whois_msg_display(ircform,f"{nick} has been idle for {idle_time}")

	def irc_RPL_WHOISSERVER(self, prefix, params):
		nick = params[1]
		server = params[2]
		whois_msg_display(ircform,f"{nick} is connected to {server}")

	def irc_RPL_ENDOFWHOIS(self, prefix, params):
		nick = params[1]
		system_msg_display(ircform,f"End of whois data for {nick}")

	def irc_RPL_WHOWASUSER(self, prefix, params):
		nick = params[1]
		username = params[2]
		host = params[3]
		realname = params[5]
		whois_msg_display(ircform,f"{nick}({username})'s host was {host}")

	def irc_RPL_ENDOFWHOWAS(self, prefix, params):
		nick = params[1]
		system_msg_display(ircform,f"End of whowas data for {nick}")

	def irc_RPL_WHOREPLY(self, prefix, params):
		channel = params[1]
		username = params[2]
		host = params[3]
		server = params[4]
		nick = params[5]
		hr = params[7].split(' ')
		if len(hr) >= 2:
			hopcount = hr[0]
			realname = hr[1]
			whois_msg_display(ircform,f"{channel} {nick}: Username: {username}, Realname: {realname}, Host: {host}, Server: {server}, Hops: {hopcount}")
		else:
			whois_msg_display(ircform,f"{channel} {nick}: Username: {username}, Host: {host}, Server: {server}")

	def irc_RPL_ENDOFWHO(self, prefix, params):
		nick = params[1]
		system_msg_display(ircform,f"End of who data for {nick}")

	def irc_RPL_INVITING(self, prefix, params):
		channel = params[1]
		nick = params[2]
		system_msg_display(ircform,f"Invitation to {channel} sent to {nick}")

	def irc_RPL_VERSION(self, prefix, params):
		sversion = params[1]
		server = params[2]
		whois_msg_display(ircform,f"Server version: {sversion}")

	def irc_RPL_CHANNELMODEIS(self, prefix, params):
		channel = params[1]
		if params[2] == '+' or params[2] == '-':
			whois_msg_display(ircform,f"{channel} has no modes set")
			return
		modes = f"{params[2]} {params[3]}"
		whois_msg_display(ircform,f"{channel} mode(s): {modes}")

	def irc_RPL_YOUREOPER(self, prefix, params):
		whois_msg_display(ircform,f"You are now an IRC operator")

	def irc_RPL_TIME(self, prefix, params):
		t = params[2]
		whois_msg_display(ircform,f"Server time/date: {t}")

	def irc_RPL_INFO(self, prefix, params):
		whois_msg_display(ircform,f"{params[1]}")


	def irc_RPL_ENDOFINFO(self, prefix, params):
		system_msg_display(ircform,f"End of info data")

	def irc_RPL_LIST(self, prefix, params):
		chan = params[1]
		crowd = params[2]
		topic = params[3]
		if topic == ' ':
			if int(crowd) > 1:
				whois_msg_display(ircform,f"{chan} ({crowd} users)")
			else:
				whois_msg_display(ircform,f"{chan} (1 user)")
		else:
			topic = topic.strip()
			if int(crowd) > 1:
				whois_msg_display(ircform,f"{chan} ({crowd} users): \"{topic}\"")
			else:
				whois_msg_display(ircform,f"{chan} ({crowd} users): \"{topic}\"")

	def irc_RPL_LISTSTART(self, prefix, params):
		system_msg_display(ircform,f"Start of list data")

	def irc_RPL_LISTEND(self, prefix, params):
		system_msg_display(ircform,f"End of list data")

	def lineReceived(self, line):
		try:
			line2 = line.decode("UTF-8")
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		d = line2.split(" ")
		if len(d) >= 2:
			if d[1].isalpha(): return irc.IRCClient.lineReceived(self, line)
		if "Cannot join channel (+k)" in line2:
			error_msg_display(ircform,f"Cannot join {CHANNEL} (wrong or missing password)")
			self.join(DEFAULT_CHANNEL)
		if "Cannot join channel (+l)" in line2:
			error_msg_display(ircform,f"Cannot join {CHANNEL} (channel is full)")
			self.join(DEFAULT_CHANNEL)
		if "Cannot join channel (+b)" in line2:
			error_msg_display(ircform,f"Cannot join {CHANNEL} (banned)")
			self.join(DEFAULT_CHANNEL)
		if "Cannot join channel (+i)" in line2:
			error_msg_display(ircform,f"Cannot join {CHANNEL} (channel is invite only)")
			self.join(DEFAULT_CHANNEL)
		if "not an IRC operator" in line2:
			error_msg_display(ircform,"Permission denied (you're not an IRC operator")
		if "not channel operator" in line2:
			error_msg_display(ircform,"Permission denied (you're not channel operator)")
		if "is already on channel" in line2:
			error_msg_display(ircform,"Invite failed (user is already in channel)")
		if "not on that channel" in line2:
			error_msg_display(ircform,"Permission denied (you're not in channel)")
		if "aren't on that channel" in line2:
			error_msg_display(ircform,"Permission denied (target user is not in channel)")
		if "have not registered" in line2:
			error_msg_display(ircform,"You're not registered")
		if "may not reregister" in line2:
			error_msg_display(ircform,"You can't reregister")
		if "enough parameters" in line2:
			error_msg_display(ircform,"Error: not enough parameters supplied to command")
		if "isn't among the privileged" in line2:
			error_msg_display(ircform,"Registration refused (server isn't setup to allow connections from your host)")
		if "Password incorrect" in line2:
			error_msg_display(ircform,"Permission denied (incorrect password)")
		if "banned from this server" in line2:
			error_msg_display(ircform,"You are banned from this server")
		if "kill a server" in line2:
			error_msg_display(ircform,"Permission denied (you can't kill a server)")
		if "O-lines for your host" in line2:
			error_msg_display(ircform,"Error: no O-lines for your host")
		if "Unknown MODE flag" in line2:
			error_msg_display(ircform,"Error: unknown MODE flag")
		if "change mode for other users" in line2:
			error_msg_display(ircform,"Permission denied (can't change mode for other users)")
		#print(line)
		return irc.IRCClient.lineReceived(self, line)

class QuircConnectionFactory(protocol.ClientFactory):
	def __init__(self):
		self.config = 0

	def buildProtocol(self, addr):
		global bot
		bot = QuircClientConnection()
		bot.factory = self
		return bot

	def clientConnectionLost(self, connector, reason):
		pass

	def clientConnectionFailed(self, connector, reason):
		pass

def fetch_userlist(irc_obj):
	global CHANNEL_USER_LIST
	CHANNEL_USER_LIST = []
	irc_obj.sendLine("NAMES %s" % CHANNEL)

# =====================
# | SUPPORT FUNCTIONS |
# =====================

def format_links(txt):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)

	# scrub html
	clean = re.compile('<.*?>')
	txt = re.sub(clean, '', txt)
	
	for u in urls:
		link = f"<b><i><a href=\"{u}\">{u}</a></i></b>"
		txt = txt.replace(u,link)
	return txt

def pretty_time(t):
	sec = timedelta(seconds=(int(t)))
	return str(sec)

def sort_nicks(nicklist):
	global CLIENT_IS_OPERATOR
	CLIENT_IS_OPERATOR = False
	global NICKNAME
	ops = []
	voiced = []
	normal = []
	sortnicks = []
	meop = f"@{NICKNAME}"
	for nick in nicklist:
		if nick == meop:
			CLIENT_IS_OPERATOR = True
		if '@' in nick:
			ops.append(nick)
		elif '+' in nick:
			voiced.append(nick)
		else:
			normal.append(nick)
	for nick in ops:
		sortnicks.append(nick)
	for nick in voiced:
		sortnicks.append(nick)
	for nick in normal:
		sortnicks.append(nick)
	return sortnicks

def display_help(obj):
	global FIRST_START_UP

	write_to_display(obj,f"<font style=\"background-color:gray;\"><br><b>{APPLICATION} {VERSION} Commands</b><br>")

	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/connect</b> SERVER PORT        -  <i>Connect to an IRC server</i></p>")
	if IRC_SSL:
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/ssl</b> SERVER PORT        -  <i>Connect to an IRC server via SSL</i></p>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/exit</b>        -  <i>Exits Quirc</i></p>")

	if RUN_IN_GADGET_MODE:
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/move X Y</b>               -  <i>Moves the IRC gadget</i>")
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/size WIDTH HEIGHT</b>      -  <i>Resizes the IRC gadget</i>")

	if not FIRST_START_UP:
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/script</b> FILENAME      -  <i>Loads a list of Quirc commands from a file and executes them</i>")
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/delay</b> TIME COMMAND      -  <i>Delays execution of a command by TIME seconds</i>")
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/var</b> NAME VALUE      -  <i>Creates a script variable</i>")
	else:
		FIRST_START_UP = False

	if not CONNECTED: return
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/nick</b> NEWNICK        -  <i>Change nickname</i></p>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/msg</b> TARGET MESSAGE  -  <i>Sends a private message</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/me</b> ACTION           -  <i>Sends a CTCP action message</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/join</b> CHANNEL [KEY]  -  <i>Joins a new channel</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/mode</b> TARGET MODE ARGUMENTS      -  <i>Sets a channel or user mode</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/oper</b> USERNAME PASSWORD      -  <i>Logs into an operator account</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/list</b> [CHANNEL] [...]      -  <i>Requests channel information from the servert</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/away</b> [MESSAGE]      -  <i>Sets status to away</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/back</b>                -  <i>Sets status to back</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/invite</b> NICKNAME CHANNEL      -  <i>Sends a channel invitation</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/whois</b> NICKNAME      -  <i>Requests whois data from the server</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/whowas</b> NICKNAME      -  <i>Requests whowas data from the server</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/who</b> SEARCH      -  <i>Search for users</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/version</b>                -  <i>Requests software version from the server</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/quit</b> [MESSAGE]      -  <i>Quits IRC</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/time</b>                -  <i>Requests the server date/time</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/info</b>                -  <i>Requests the server info text</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/uptime</b>                -  <i>Displays application uptime</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/raw</b> [MESSAGE]      -  <i>Sends an unaltered message to the server</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><b>/print</b> [TEXT]      -  <i>Prints text on the chat display</i>")
	if CLIENT_IS_OPERATOR:
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/topic</b> TEXT          -  <i>Sets the current channel's topic</i>")
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/key</b> TEXT            -  <i>Sets the current channel's key</i>")
		write_to_display(obj,"<font style=\"background-color:gray;\"><b>/nokey</b>               -  <i>Unsets the current channel's key</i>")
	write_to_display(obj,"<font style=\"background-color:gray;\"><br>To send more than one command at a time, chain them together with \"&&\"<br>")

def add_script_variable(var,val):
	global SCRIPT_VARIABLES
	found = False
	lv = []
	for v in SCRIPT_VARIABLES:
		if v[0] == var:
			v[1] = val
			lv.append(v)
			found = True
		else:
			lv.append(v)
	if found:
		SCRIPT_VARIABLES = lv
		return
	e = [var,val]
	lv.append(e)
	SCRIPT_VARIABLES = lv

def interpolate_variables(txt):
	global SERVER
	global PORT
	global CHANNEL
	global NICKNAME
	global UPTIME
	global SCRIPT_VARIABLES
	iserv = re.compile(re.escape('$server'), re.IGNORECASE)
	txt = iserv.sub(SERVER,txt)
	iport = re.compile(re.escape('$port'), re.IGNORECASE)
	txt = iport.sub(str(PORT),txt)
	ichan = re.compile(re.escape('$channel'), re.IGNORECASE)
	txt = ichan.sub(CHANNEL,txt)
	inick = re.compile(re.escape('$nickname'), re.IGNORECASE)
	txt = inick.sub(NICKNAME,txt)
	itime = re.compile(re.escape('$uptime'), re.IGNORECASE)
	txt = itime.sub(str(UPTIME),txt)

	for v in SCRIPT_VARIABLES:
		iv = re.compile(re.escape(f"${v[0]}"), re.IGNORECASE)
		txt = iv.sub(v[1],txt)

	return txt

def handle_commands(obj,text):
	text = text.strip()
	text = interpolate_variables(text)
	tokens = text.split()
	global NICKNAME
	global CHANNEL
	global CLIENT_IS_AWAY
	global CHANNEL_KEY
	global CONNECTED
	global bot
	global SERVER
	global PORT

	if '&&' in text:
		cmds = text.split('&&')
		for c in cmds:
			c = c.strip()
			if not handle_commands(obj,c):
				error_msg_display(obj,f"Error executing command: \"{c}\"")
				return True
		return True

	if len(tokens) >= 3 and tokens[0] == "/var":
		tokens.pop(0)
		var = tokens.pop(0)
		val = ' '.join(tokens)
		add_script_variable(var,val)
		return True

	if len(tokens) >= 3 and tokens[0] == "/delay":
		tokens.pop(0)
		t = int(tokens.pop(0))
		c = ' '.join(tokens)
		obj.delay_script(t,c)
		return True

	if len(tokens) == 1 and tokens[0] == '/script':
		fname, _ = QFileDialog.getOpenFileName(obj,"Open Quirc Script", "","All Files (*);;Text Files (*.txt);;Quirc Script Files (*.quirc)")
		if(fname):
			obj.irc_input.setText(f"/script {fname}")
		return True

	if len(tokens) == 2 and tokens[0] == '/script':
		script = open(tokens[1],"r")
		for line in script:
			line = line.strip()
			# Handle script comments
			if len(line) >= 1 and line[0] == SCRIPT_COMMENT_SYMBOL:
				continue
			if SCRIPT_COMMENT_SYMBOL in line:
				i = line.find(SCRIPT_COMMENT_SYMBOL)
				line = line[:i]
			# Blank line
			if len(line) == 0: continue
			# Execution
			if not handle_commands(obj,line):
				error_msg_display(obj,f"Error executing scripted command: \"{line}\"")
				return True
		return True

	if len(tokens) >= 2 and tokens[0] == "/print":
		tokens.pop(0)
		write_to_display(obj,f"{' '.join(tokens)}")
		return True

	if IRC_SSL:
		if len(tokens) == 3 and tokens[0] == "/ssl":
			if CONNECTED:
				bot.quit()
				CONNECTED = False
				empty_userlist(obj)
				obj.channel.setText("")
				obj.topic.setText(f"{NO_TOPIC}")
				system_msg_display(obj,"Disconnected.")
			SERVER = tokens[1]
			PORT = tokens[2]
			bot = QuircConnectionFactory()
			reactor.connectSSL(SERVER,int(PORT),bot,ssl.ClientContextFactory())
			return True

	if len(tokens) == 3 and tokens[0] == "/connect":
		if CONNECTED:
			bot.quit()
			CONNECTED = False
			empty_userlist(obj)
			obj.channel.setText("")
			obj.topic.setText(f"{NO_TOPIC}")
			system_msg_display(obj,"Disconnected.")
		SERVER = tokens[1]
		PORT = tokens[2]
		bot = QuircConnectionFactory()
		reactor.connectTCP(SERVER, int(PORT), bot)
		return True

	if len(tokens) == 1 and tokens[0] == "/uptime":
		t = pretty_time(UPTIME)
		system_msg_display(obj,f"Uptime: {str(t)}")
		return True

	if len(tokens) >= 1 and tokens[0] == "/help":
		display_help(obj)
		return True

	if len(tokens) >= 1 and tokens[0] == "/exit":
		app.quit()
		return True

	if not CONNECTED: return

	if len(tokens) >= 2 and tokens[0] == "/list":
		tokens.pop(0)
		chans = ','.join(tokens)
		bot.sendLine(f"LIST {chans}")
		system_msg_display(obj,f"Requested list data for {chans}")
		return True

	if len(tokens) == 1 and tokens[0] == "/list":
		bot.sendLine(f"LIST")
		system_msg_display(obj,f"Requested list data for all channels")
		return True

	if len(tokens) == 1 and tokens[0] == "/info":
		bot.sendLine("INFO")
		return True

	if len(tokens) == 1 and tokens[0] == "/time":
		bot.sendLine("TIME")
		return True

	if len(tokens) >= 3 and tokens[0] == "/oper":
		tokens.pop(0)
		username = tokens.pop(0)
		password = ' '.join(tokens)
		bot.sendLine(f"OPER {username} {password}")
		return True

	if len(tokens) >= 1 and tokens[0] == "/mode":
		if len(tokens) == 1:
			bot.sendLine(f"MODE {CHANNEL}")
			return True
		tokens.pop(0)
		if len(tokens) >= 3:
			target = tokens.pop(0)
			mod = tokens.pop(0)
			p = ' '.join(tokens)
			bot.sendLine(f"MODE {target} {mod} {p}")
			return True
		elif len(tokens) == 2:
			target = tokens.pop(0)
			mod = tokens.pop(0)
			bot.sendLine(f"MODE {target} {mod}")
			return True
		else:
			error_msg_display(obj,f"Unrecognized mode: {' '.join(tokens)}")
			return True

	if len(tokens) == 1 and tokens[0] == "/version":
		bot.sendLine("VERSION")
		system_msg_display(obj,f"Requested version data")
		return True

	if len(tokens) >= 2 and tokens[0] == "/who":
		tokens.pop(0)
		bot.sendLine(f"WHO {' '.join(tokens)}")
		system_msg_display(obj,f"Requested who data")
		return True

	if len(tokens) == 2 and tokens[0] == "/whowas":
		bot.sendLine(f"WHOWAS {tokens[1]}")
		system_msg_display(obj,f"Requested whowas data for {NICKNAME}")
		return True

	if len(tokens) == 2 and tokens[0] == "/whois":
		NICKNAME = tokens[1]
		bot.whois(NICKNAME)
		system_msg_display(obj,f"Requested whois data for {NICKNAME}")
		return True

	if len(tokens) == 2 and tokens[0] == "/invite":
		target = tokens[1]
		bot.sendLine(f"INVITE {target} {CHANNEL}")
		return True

	if len(tokens) == 3 and tokens[0] == "/invite":
		target = tokens[1]
		chan = tokens[2]
		bot.sendLine(f"INVITE {target} {chan}")
		return True

	if RUN_IN_GADGET_MODE:
		if len(tokens) == 3 and tokens[0] == "/move":
			new_x = int(tokens[1])
			new_y = int(tokens[2])
			obj.move(new_x,new_y)
			return True
		if len(tokens) == 3 and tokens[0] == "/size":
			new_x = int(tokens[1])
			new_y = int(tokens[2])
			obj.resize(new_x,new_y)
			return True

	if len(tokens) == 1 and tokens[0] == "/back":
		if CLIENT_IS_AWAY:
			bot.back()
			CLIENT_IS_AWAY = False
			system_msg_display(obj,"Status set to 'back'")
		else:
			system_msg_display(obj,"Status is not set to 'away'")
		return True

	if len(tokens) >= 1 and tokens[0] == "/away":
		if len(tokens) > 1:
			if CLIENT_IS_AWAY:
				bot.back()
				CLIENT_IS_AWAY = False
				system_msg_display(obj,"Status set to 'back'")
			else:
				tokens.pop(0)
				MSG = " ".join(tokens)
				bot.away(message=MSG)
				CLIENT_IS_AWAY = True
				system_msg_display(obj,f"Status set to 'away' ({MSG})")
			return True
		else:
			if CLIENT_IS_AWAY:
				bot.back()
				CLIENT_IS_AWAY = False
				system_msg_display(obj,"Status set to 'back'")
			else:
				bot.away()
				CLIENT_IS_AWAY = True
				system_msg_display(obj,"Status set to 'away'")
			return True

	if len(tokens) >= 2 and tokens[0] == "/raw":
		tokens.pop(0)
		MSG = " ".join(tokens)
		bot.sendLine(MSG)
		return True

	if len(tokens) == 2 and tokens[0] == "/nick":
		NICKNAME = tokens[1]
		bot.setNick(NICKNAME)
		fetch_userlist(bot)
		system_msg_display(obj,f"You are now known as {NICKNAME}")
		update_server_label(ircform)
		return True

	if len(tokens) >= 1 and tokens[0] == "/quit":
		if len(tokens) > 1:
			tokens.pop(0)
			MSG = " ".join(tokens)
			bot.quit(message=MSG)
			empty_userlist(obj)
			obj.channel.setText("")
			system_msg_display(obj,"Disconnected.")
			obj.topic.setText(f"{NO_TOPIC}")
		else:
			bot.quit()
			empty_userlist(obj)
			obj.channel.setText("")
			system_msg_display(obj,"Disconnected.")
			obj.topic.setText(f"{NO_TOPIC}")
		return True

	if len(tokens) >= 2 and tokens[0] == "/join":
		if len(tokens) == 2:
			bot.part(CHANNEL)
			CHANNEL = tokens[1]
			obj.channel.setText(" ")
			obj.topic.setText(f"{NO_TOPIC}")
			bot.join(CHANNEL)
		elif len(tokens) > 2:
			tokens.pop(0)
			bot.part(CHANNEL)
			CHANNEL = tokens[0]
			tokens.pop(0)
			cKey = " ".join(tokens)
			obj.channel.setText(" ")
			obj.topic.setText(f"{NO_TOPIC}")
			bot.join(CHANNEL,key=cKey)
		return True

	if len(tokens) >= 3 and tokens[0] == "/msg":
		tokens.pop(0)
		TARGET = tokens.pop(0)
		MSG = " ".join(tokens)
		bot.msg(TARGET,MSG)
		private_msg_display(obj,bot.nickname,MSG)
		return True

	if len(tokens) >= 2 and tokens[0] == "/me":
		tokens.pop(0)
		MSG = " ".join(tokens)
		bot.msg(CHANNEL,f"\x01ACTION {MSG}\x01")
		action_msg_display(obj,bot.nickname,MSG)
		return True

	if len(tokens) >= 2 and tokens[0] == "/topic":
		if not CLIENT_IS_OPERATOR:
			error_msg_display(obj,"Only operators can change the channel topic")
			return True
		tokens.pop(0)
		MSG = " ".join(tokens)
		bot.topic(CHANNEL,topic=f"{MSG}")
		return True

	if len(tokens) >= 3 and tokens[0] == "/notice":
		tokens.pop(0)
		TARGET = tokens.pop(0)
		MSG = " ".join(tokens)
		bot.notice(TARGET,MSG)
		notice_msg_display(obj,bot.nickname,MSG)
		return True

	if len(tokens) >= 2 and tokens[0] == "/key":
		if not CLIENT_IS_OPERATOR:
			error_msg_display(obj,"Only operators can set a channel key")
			return True
		tokens.pop(0)
		MSG = " ".join(tokens)
		CHANNEL_KEY = MSG
		bot.mode(CHANNEL,True,"k",user=f"{MSG}")
		system_msg_display(obj,f"Channel key set to '{MSG}'")
		return True

	if len(tokens) >= 1 and tokens[0] == "/nokey":
		if not CLIENT_IS_OPERATOR:
			error_msg_display(obj,"Only operators can remove a channel key")
			return True
		bot.mode(CHANNEL,False,"k",user=f"{CHANNEL_KEY}")
		system_msg_display(obj,"Channel key removed")
		return True

	return False

def handle_user_input( obj, text ):
	if handle_commands(obj,text):
		return
	if len(text) >= 1:
		if text[0] == '/':
			error_msg_display(obj,f"Unrecognized command: \"{text}\"")
			return
	if not CONNECTED:
		if IRC_SSL:
			error_msg_display(obj,f"Not connected to a server. Use /connect or /ssl to connect to one")
		else:
			error_msg_display(obj,f"Not connected to a server. Use /connect to connect to one")
		return
	chat_msg_display(obj,bot.nickname,text)
	bot.msg(CHANNEL,text,length=MAXIMUM_IRC_MESSAGE_LENGTH)

def private_msg_display( obj, user, text ):
	if CREATE_LINKS:
		text = format_links(text)
	obj.chat_display.append(f"{PRIVATE_MESSAGE_SYMBOL}<b><font color={PRIVATE_MESSAGE_COLOR}><u>{user}</u></font>  </b>{text}\n")

def chat_msg_display( obj, user, text ):
	if CREATE_LINKS:
		text = format_links(text)
	obj.chat_display.append(f"{PUBLIC_MESSAGE_SYMBOL}<font color={PUBLIC_MESSAGE_COLOR}><b><u>{user}</u></b></font>  {text}\n")

def system_msg_display( obj, text ):
	obj.chat_display.append(f"<b>{SYSTEM_MESSAGE_SYMBOL}<i><font color={SYSTEM_MESSAGE_COLOR}> {text}</i></b></font>\n")

def notice_msg_display( obj, user, text ):
	obj.chat_display.append(f"<b>{NOTICE_MESSAGE_SYMBOL}<font color={NOTICE_MESSAGE_COLOR}><u>{user}</u></b></font>  {text}\n")

def action_msg_display( obj, user, text ):
	obj.chat_display.append(f"<b><font color={CTCP_ACTION_MESSAGE_COLOR}>{PUBLIC_MESSAGE_SYMBOL}<i><u>{user}</u> {text}</font></i></b>\n")

def whois_msg_display( obj, text ):
	obj.chat_display.append(f"{WHOIS_MESSAGE_SYMBOL}<b><font color={WHOIS_MESSAGE_COLOR}></font>  </b>{text}\n")

def error_msg_display( obj, text ):
	obj.chat_display.append(f"{ERROR_MESSAGE_SYMBOL}<b><font color={ERROR_MESSAGE_COLOR}>  {text}</font></b>\n")

def write_to_display( obj, text ):
	obj.chat_display.append(text)

def add_to_user_list( obj, text ):
	items = obj.user_list.findItems(text,Qt.MatchExactly)
	if len(items) > 0:
		return
	obj.user_list.addItem(text)

def empty_userlist( obj ):
	obj.user_list.clear()

def get_userlist( obj ):
	items = []
	ulist = []
	for index in range(obj.user_list.count()):
		items.append(obj.user_list.item(index))
	for item in items:
		ulist.append(item.text())
	return ulist

def remove_from_user_list( obj, text ):
	items = obj.user_list.findItems(text,Qt.MatchExactly)
	if len(items) > 0:
		for item in items:
			obj.user_list.takeItem(obj.user_list.row(item))

def update_server_label(obj):
	if CONNECTED:
		obj.server.setText(f"Connected to {SERVER}:{PORT}")
	else:
		obj.server.setText(" ")

# ================
# | MAIN PROGRAM |
# ================

if __name__ == '__main__':
	global FIRST_START_UP
	FIRST_START_UP = True

	global ircform
	ircform = Quirc_IRC_Client()

	if STARTUP_SCRIPT != '':
		handle_commands(ircform,f"/script {STARTUP_SCRIPT}")

	reactor.run()
