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
VERSION = "0.01548"
DESCRIPTION = "A Python/Qt5 IRC client"

# ========================
# | IRC NETWORK SETTINGS |
# ========================

SERVER = "localhost"
PORT = 6667
CHANNEL = "#quirc"
CHANNEL_PASSWORD = ""
DEFAULT_CHANNEL = "#quirc"

NICKNAME = "quirc"
REALNAME = f"{APPLICATION} IRC Client v{VERSION}"
USERNAME = "quirc"

# =======================
# | IRC CLIENT SETTINGS |
# =======================

PUBLIC_MESSAGE_COLOR = "blue"
PRIVATE_MESSAGE_COLOR = "red"
SYSTEM_MESSAGE_COLOR = "grey"
CTCP_ACTION_MESSAGE_COLOR = "green"
NOTICE_MESSAGE_COLOR = "purple"
CLIENT_FONT = "Courier New"

OPERATOR_COLOR = "green"
VOICED_COLOR = "blue"
USER_COLOR = "black"

RUN_IN_GADGET_MODE = False
GADGET_X = 0
GADGET_Y = 0
GADGET_WIDTH = 600
GADGET_HEIGHT = 600
GADGET_ALWAYS_ON_TOP = False

# ================================
# | HANDLE COMMANDLINE ARGUMENTS |
# ================================

import argparse
parser = argparse.ArgumentParser(prog=f"python quirc.py", description=f"{APPLICATION} {VERSION} - {DESCRIPTION}")
parser.add_argument("server", help="IRC server to connect to")
parser.add_argument("port", help="IRC port to connect to", type=int)

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

parser.add_argument("-C","--chat", help="Set chat message display color (default: blue)")
parser.add_argument("-P","--private", help="Set private message display color (default: red)")
parser.add_argument("-s","--system", help="Set system message display color (default: grey)")
parser.add_argument("-a","--action", help="Set action message display color (default: green)")
parser.add_argument("-N","--notice", help="Set notice message display color (default: purple)")
parser.add_argument("-f","--font", help="Set display font (default: Courier New)")

args = parser.parse_args()
SERVER = args.server
PORT = args.port

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

if args.chat:
	PUBLIC_MESSAGE_COLOR = args.chat
if args.private:
	PRIVATE_MESSAGE_COLOR = args.private
if args.system:
	SYSTEM_MESSAGE_COLOR = args.system
if args.action:
	CTCP_ACTION_MESSAGE_COLOR = args.action
if args.notice:
	NOTICE_MESSAGE_COLOR = args.notice
if args.font:
	CLIENT_FONT = args.font

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

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

import qt5reactor
qt5reactor.install()
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

# ==============================
# | WIDGET SIZES AND LOCATIONS |
# ==============================

input_height = 20
output_width = 440
output_height = 400
text_x = 10
user_width = 150
user_height = 400
user_x = text_x + output_width + 10
input_width = output_width + user_width + 10
window_width = output_width + user_width + 30
window_height = output_height + input_height + 30
text_y = 30
output_y = 5

# =====================
# | RUN TIME SETTINGS |
# =====================

PUBLIC_MESSAGE_SYMBOL = f"<font color=\"{PUBLIC_MESSAGE_COLOR}\">&#9679;</font> "
SYSTEM_MESSAGE_SYMBOL = f"<font color=\"{SYSTEM_MESSAGE_COLOR}\">&#9679;</font> "
PRIVATE_MESSAGE_SYMBOL = f"<font color=\"{PRIVATE_MESSAGE_COLOR}\">&#9679;</font> "
NOTICE_MESSAGE_SYMBOL = f"<font color=\"{NOTICE_MESSAGE_COLOR}\">&#9679;</font> "

CLIENT_IS_OPERATOR = False
CLIENT_IS_AWAY = False
TOPIC = "No topic"
CHANNEL_KEY = CHANNEL_PASSWORD

LOGO = """ ██████╗ ██╗   ██╗██╗██████╗  ██████╗
██╔═══██╗██║   ██║██║██╔══██╗██╔════╝
██║   ██║██║   ██║██║██████╔╝██║     
██║▄▄ ██║██║   ██║██║██╔══██╗██║     
╚██████╔╝╚██████╔╝██║██║  ██║╚██████╗
 ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝"""

# ============================
# | GRAPHICAL USER INTERFACE |
# ============================

class Quirc_IRC_Client(QWidget):

	def __init__(self):
		super().__init__()
		self.createQuircUI()

	# Handle window resizing
	def resizeEvent(self,resizeEvent):
		rwindow_width = self.width()
		rwindow_height = self.height()
		self.user_list.setGeometry(QtCore.QRect(rwindow_width-user_width-10, text_y, user_width, rwindow_height-60))
		self.channel.setGeometry(QtCore.QRect(rwindow_width-user_width-10, text_y-30, user_width, self.channel.height()))
		self.chat_display.setGeometry(QtCore.QRect(text_x, text_y, rwindow_width-self.user_list.width()-20, rwindow_height-60))
		self.topic.setGeometry(QtCore.QRect(text_x, text_y-30, rwindow_width-self.user_list.width()-25, self.topic.height()))
		self.irc_input.setGeometry(QtCore.QRect(text_x, text_y+self.chat_display.height()+5, rwindow_width-20, input_height))

	def user_input(self):
		handle_user_input(self,self.irc_input.text())
		self.irc_input.setText('')

	def closeEvent(self, event):
		app.quit()

	def changeTitle(self,text):
		self.setWindowTitle(text)

	def createQuircUI(self):

		self.setWindowTitle("Disconnected")

		font = QFont(CLIENT_FONT, 10)
		channel_and_topic_font = QFont(CLIENT_FONT, 10, QFont.Bold)
		userfont = QFont(CLIENT_FONT, 10, QFont.Bold)

		# Channel name display
		self.channel = QLabel(self)
		self.channel.setText(f"{CHANNEL}")
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
		
		# Channel user list
		self.user_list = QListWidget(self)
		self.user_list.setGeometry(QtCore.QRect(user_x, text_y, user_width, user_height))
		self.user_list.setObjectName("user_list")
		self.user_list.setFont(userfont)
		self.user_list.installEventFilter(self)

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
				source is self.topic):
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
				copyAct = menu.addAction('Copy users to clipboard')
				action = menu.exec_(self.user_list.mapToGlobal(event.pos()))

				target = item.text()
				target = target.replace("@","")
				target = target.replace("+","")

				if action == kickAct:
					bot.kick(CHANNEL,target)
					bot.sendLine("NAMES %s" % CHANNEL)
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
				copyAct = menu.addAction('Copy users to clipboard')
				action = menu.exec_(self.user_list.mapToGlobal(event.pos()))

				target = item.text()
				target = target.replace("@","")
				target = target.replace("+","")

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
		irc.IRCClient.connectionMade(self)
		ircform.changeTitle(f"{SERVER}:{PORT}")
		system_msg_display(ircform,f"Connecting to {SERVER}:{PORT}")

	def connectionLost(self, reason):
		system_msg_display(ircform,"Connection lost.")
		irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		system_msg_display(ircform,"Connected!")
		self.join(CHANNEL, CHANNEL_PASSWORD)

	def joined(self, channel):
		ircform.channel.setText(f"{channel}")
		self.sendLine("NAMES %s" % channel)
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
					self.sendLine("NAMES %s" % channel)
			else:
				for u in args:
					system_msg_display(ircform,f"{pnick} took operator status from {u}")
					self.sendLine("NAMES %s" % channel)
		if 'v' in modes:
			if set:
				for u in args:
					system_msg_display(ircform,f"{pnick} gave {u} voiced status")
					self.sendLine("NAMES %s" % channel)
			else:
				for u in args:
					system_msg_display(ircform,f"{pnick} took voiced status from {u}")
					self.sendLine("NAMES %s" % channel)
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
		self.sendLine("NAMES %s" % CHANNEL)

	def userJoined(self, user, channel):
		system_msg_display(ircform,f"{user} joined {channel}")
		self.sendLine("NAMES %s" % channel)

	def userLeft(self, user, channel):
		system_msg_display(ircform,f"{user} left {channel}")
		self.sendLine("NAMES %s" % channel)

	def afterCollideNick(self, nickname):
		global NICKNAME
		NICKNAME = nickname + random.randint(100, 999)
		system_msg_display(ircform,f"Nickname is now {NICKNAME}")
		return NICKNAME

	def userRenamed(self, oldname, newname):
		system_msg_display(ircform,f"User {oldname} changed their nick to {newname}")
		self.sendLine("NAMES %s" % CHANNEL)

	def topicUpdated(self, user, channel, newTopic):
		global TOPIC
		system_msg_display(ircform,f"User {user} set topic on {channel} to '{newTopic}'")
		if newTopic == "" or newTopic.isspace():
			TOPIC = "No topic"
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

	def irc_RPL_NAMREPLY(self, prefix, params):
		channel = params[2].lower()
		nicklist = params[3].split(' ')
		empty_userlist(ircform)
		for nick in nicklist:
			add_to_user_list(ircform,nick)

	def irc_RPL_ENDOFNAMES(self, prefix, params):
		ulist = get_userlist(ircform)
		ulist = sort_nicks(ulist)
		empty_userlist(ircform)
		for nick in ulist:
			add_to_user_list(ircform,nick)


	def irc_RPL_TOPIC(self, prefix, params):
		global TOPIC
		if not params[2].isspace():
			TOPIC = params[2]
			ircform.topic.setText(f"{TOPIC}")
		else:
			TOPIC = "No topic"
			ircform.topic.setText(f"{TOPIC}")

	def lineReceived(self, line):
		try:
			line2 = line.decode("UTF-8")
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		if "Cannot join channel" in line2:
			system_msg_display(ircform,f"Cannot join {CHANNEL} (wrong or missing password)")
			self.join(DEFAULT_CHANNEL)
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

# =====================
# | SUPPORT FUNCTIONS |
# =====================

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
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/nick</b> NEWNICK        -  <i>Change nickname</i></p>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/msg</b> TARGET MESSAGE  -  <i>Sends a private message</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/me</b> ACTION           -  <i>Sends a CTCP action message</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/join</b> CHANNEL [KEY]  -  <i>Joins a new channel</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/away</b> [MESSAGE]      -  <i>Sets status to away</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/back</b>                -  <i>Sets status to back</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/invite</b> NICKNAME CHANNEL      -  <i>Sends a channel invitation</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/quit</b> [MESSAGE]      -  <i>Quits IRC</i>")
	write_to_display(obj,"<font style=\"background-color:silver;\"><b>/raw</b> [MESSAGE]      -  <i>Sends an unaltered message to the server</i>")
	if CLIENT_IS_OPERATOR:
		write_to_display(obj,"<font style=\"background-color:silver;\"><b>/topic</b> TEXT          -  <i>Sets the current channel's topic</i>")
		write_to_display(obj,"<font style=\"background-color:silver;\"><b>/key</b> TEXT            -  <i>Sets the current channel's key</i>")
		write_to_display(obj,"<font style=\"background-color:silver;\"><b>/nokey</b>               -  <i>Unsets the current channel's key</i>")
	if RUN_IN_GADGET_MODE:
		write_to_display(obj,"<font style=\"background-color:silver;\"><b>/move X Y</b>               -  <i>Moves the IRC gadget</i>")
		write_to_display(obj,"<font style=\"background-color:silver;\"><b>/size WIDTH HEIGHT</b>      -  <i>Resizes the IRC gadget</i>")

def handle_commands(obj,text):
	tokens = text.split()
	global NICKNAME
	global CHANNEL
	global CLIENT_IS_AWAY
	global CHANNEL_KEY

	if len(tokens) == 3 and tokens[0] == "/invite":
		target = tokens[1]
		chan = tokens[2]
		bot.sendLine(f"INVITE {target} {chan}")
		system_msg_display(obj,f"Invitation to {chan} sent to {target}")
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

	if len(tokens) >= 1 and tokens[0] == "/help":
		display_help(obj)
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
		bot.sendLine("NAMES %s" % CHANNEL)
		system_msg_display(obj,f"You are now known as {NICKNAME}")
		return True

	if len(tokens) >= 1 and tokens[0] == "/quit":
		if len(tokens) > 1:
			tokens.pop(0)
			MSG = " ".join(tokens)
			bot.quit(message=MSG)
			app.quit()
		else:
			bot.quit()
			app.quit()

	if len(tokens) >= 2 and tokens[0] == "/join":
		if len(tokens) == 2:
			bot.part(CHANNEL)
			CHANNEL = tokens[1]
			bot.join(CHANNEL)
		elif len(tokens) > 2:
			tokens.pop(0)
			bot.part(CHANNEL)
			CHANNEL = tokens[0]
			tokens.pop(0)
			cKey = " ".join(tokens)
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
			system_msg_display(obj,"Only operators can change the channel topic")
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
			system_msg_display(obj,"Only operators can set a channel key")
			return True
		tokens.pop(0)
		MSG = " ".join(tokens)
		CHANNEL_KEY = MSG
		bot.mode(CHANNEL,True,"k",user=f"{MSG}")
		system_msg_display(obj,f"Channel key set to '{MSG}'")
		return True

	if len(tokens) >= 1 and tokens[0] == "/nokey":
		if not CLIENT_IS_OPERATOR:
			system_msg_display(obj,"Only operators can remove a channel key")
			return True
		bot.mode(CHANNEL,False,"k",user=f"{CHANNEL_KEY}")
		system_msg_display(obj,"Channel key removed")
		return True

	return False

def handle_user_input( obj, text ):
	if handle_commands(obj,text):
		return
	chat_msg_display(obj,bot.nickname,text)
	bot.msg(CHANNEL,text,length=450)

def private_msg_display( obj, user, text ):
	obj.chat_display.append(f"{PRIVATE_MESSAGE_SYMBOL}<b><font color={PRIVATE_MESSAGE_COLOR}>{user}</font>  </b>{text}\n")

def chat_msg_display( obj, user, text ):
	obj.chat_display.append(f"{PUBLIC_MESSAGE_SYMBOL}<font color={PUBLIC_MESSAGE_COLOR}><b>{user}</b></font>  {text}\n")

def system_msg_display( obj, text ):
	obj.chat_display.append(f"<b>{SYSTEM_MESSAGE_SYMBOL}<i><font color={SYSTEM_MESSAGE_COLOR}> {text}</i></b></font>\n")

def notice_msg_display( obj, user, text ):
	obj.chat_display.append(f"<b>{NOTICE_MESSAGE_SYMBOL}<i><font color={NOTICE_MESSAGE_COLOR}> {user}</i></b></font>  {text}\n")

def action_msg_display( obj, user, text ):
	obj.chat_display.append(f"<b><font color={CTCP_ACTION_MESSAGE_COLOR}>{PUBLIC_MESSAGE_SYMBOL}<i> {user} {text}</font></i></b>\n")

def write_to_display( obj, text ):
	obj.chat_display.append(text)

def add_to_user_list( obj, text ):
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

# ================
# | MAIN PROGRAM |
# ================

if __name__ == '__main__':
	global ircform
	ircform = Quirc_IRC_Client()

	bot = QuircConnectionFactory()
	reactor.connectTCP(SERVER, PORT, bot)
	reactor.run()
