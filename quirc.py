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
# https://github.com/danhetrick/quirc
#
# (c) Copyright Dan Hetrick 2019
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

IS_SSL_AVAILABLE = True

import sys
import random
import os
import re
from datetime import datetime, timedelta
import json

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

import qt5reactor
qt5reactor.install()
from twisted.internet import reactor, protocol

try:
	from twisted.internet import ssl
except ImportError as error:
	IS_SSL_AVAILABLE = False

from twisted.words.protocols import irc

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

APPLICATION = "Quirc"
VERSION = "0.02670"
DESCRIPTION = "A Python3/Qt5/Twisted IRC client"

# ============
# | SETTINGS |
# ============

NICKNAME = "quirc"
REALNAME = f"{APPLICATION} {VERSION}"
USERNAME = NICKNAME

SERVER = ''
PORT = 6667
SERVER_PASSWORD = ''

DISPLAY_FONT = "Courier New"
DISPLAY_FONT_SIZE = 10

PUBLIC_MESSAGE_COLOR = "#00008B"
PRIVATE_MESSAGE_COLOR = "#FF0000"
SYSTEM_MESSAGE_COLOR = "#FFA500"
ACTION_MESSAGE_COLOR = "#008000"
NOTICE_MESSAGE_COLOR = "#800080"
ERROR_MESSAGE_COLOR = "#FF3333"
BACKGROUND_COLOR = "#FFFFFF"

MAXIMUM_NICK_DISPLAY_SIZE = 10

TURN_URLS_INTO_LINKS = True
SCRUB_HTML_FROM_INCOMING_MESSAGES = True

MAXIMUM_IRC_MESSAGE_LENGTH = 450

# =====================
# | RUN-TIME SETTINGS |
# =====================

CLIENT_IS_CONNECTED = False
CONNECTED_VIA_SSL = False
CONNECT_ON_JOIN_CHANNEL = ''
CONNECT_ON_JOIN_CHANNEL_KEY = ''
CLIENT_IS_CHANNEL_OPERATOR = False
CLIENT_IS_AWAY = False

USER_INPUT_HISTORY = ['']
USER_INPUT_HISTORY_POINTER = 0
USER_INPUT_HISTORY_MAX_SIZE = 20

CHANNEL = ''
CHANNEL_USER_LIST = []

CHANNEL_DATABASE = []
TOPIC_DATABASE = []

LOGO = """ ██████╗ ██╗   ██╗██╗██████╗  ██████╗
██╔═══██╗██║   ██║██║██╔══██╗██╔════╝
██║   ██║██║   ██║██║██████╔╝██║     
██║▄▄ ██║██║   ██║██║██╔══██╗██║     
╚██████╔╝╚██████╔╝██║██║  ██║╚██████╗
 ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝"""

INSTALL_DIRECTORY = sys.path[0]
DATA_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "data")

CONFIG_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "config")
if not os.path.isdir(CONFIG_DIRECTORY):
	try:
		os.mkdir(CONFIG_DIRECTORY)
	except OSError:
		print(f"Creation of {CONFIG_DIRECTORY} failed. Exiting...")
		app.quit()

USER_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "user.json")
SERVER_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "server.json")
COLOR_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "colors.json")
FONT_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "font.json")
CHANNEL_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "channels.json")

SERVER_LIST_FILE = os.path.join(DATA_DIRECTORY, "servers.txt")

QUIRC_ICON_FILE = os.path.join(DATA_DIRECTORY, "qicon.png")
CONNECT_ICON_FILE = os.path.join(DATA_DIRECTORY, "connect.png")
USER_ICON_FILE = os.path.join(DATA_DIRECTORY, "user.png")
COLOR_ICON_FILE = os.path.join(DATA_DIRECTORY, "colors.png")
FONT_ICON_FILE = os.path.join(DATA_DIRECTORY, "font.png")
DISCONNECT_ICON_FILE = os.path.join(DATA_DIRECTORY, "disconnect.png")
CHAT_ICON_FILE = os.path.join(DATA_DIRECTORY, "chat.png")
CLIPBOARD_ICON_FILE = os.path.join(DATA_DIRECTORY, "clipboard.png")
KICK_ICON_FILE = os.path.join(DATA_DIRECTORY, "kick.png")
BOOKMARK_ICON_FILE = os.path.join(DATA_DIRECTORY, "bookmark.png")
WHOIS_ICON_FILE = os.path.join(DATA_DIRECTORY, "whois.png")
EXIT_ICON_FILE = os.path.join(DATA_DIRECTORY, "exit.png")
WEB_ICON_FILE = os.path.join(DATA_DIRECTORY, "web.png")
AUTO_ICON_FILE = os.path.join(DATA_DIRECTORY, "auto.png")
SYSTEM_ICON_FILE = os.path.join(DATA_DIRECTORY, "system.png")
IRC_ICON_FILE = os.path.join(DATA_DIRECTORY, "irc.png")
FILE_ICON_FILE = os.path.join(DATA_DIRECTORY, "file.png")
BAN_ICON_FILE = os.path.join(DATA_DIRECTORY, "ban.png")
QUIRC_LOGO_FILE = os.path.join(DATA_DIRECTORY, "quirc.png")

FIRACODE_FONT_LOCATION = os.path.join(DATA_DIRECTORY, "FiraCode-Regular.ttf")
FIRACODE_BOLD_FONT_LOCATION = os.path.join(DATA_DIRECTORY, "FiraCode-Bold.ttf")

id = QFontDatabase.addApplicationFont(FIRACODE_FONT_LOCATION)
_fontstr = QFontDatabase.applicationFontFamilies(id)[0]
QUIRC_FONT = QFont(_fontstr, DISPLAY_FONT_SIZE)

id = QFontDatabase.addApplicationFont(FIRACODE_BOLD_FONT_LOCATION)
_fontstr = QFontDatabase.applicationFontFamilies(id)[0]
QUIRC_FONT_BOLD = QFont(_fontstr, DISPLAY_FONT_SIZE)
QUIRC_FONT_BOLD.setBold(True)

AUTO_JOIN = []

LOADED_USER_INFO_FROM_FILE = False

MESSAGE_HEIGHT = 25
MESSAGE_ICON_SPACE_WIDTH = 30

MESSAGE_ICON_WIDTH = 15
MESSAGE_ICON_HEIGHT = 15

ERROR_ICON = "error.png"
NOTICE_ICON = "chat.png"
PRIVATE_ICON = "chat.png"
ACTION_ICON = "user.png"
IRC_ICON = "irc.png"
SYSTEM_ICON = "system.png"
QUIRC_LOGO = "quirc.png"

ICON_TEMPLATE = f"""
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="width: {MESSAGE_ICON_SPACE_WIDTH}px; height: {MESSAGE_HEIGHT}px; text-align: center; vertical-align: middle;"><img src=\"!ICON!\" height=\"{MESSAGE_ICON_WIDTH}\" width=\"{MESSAGE_ICON_HEIGHT}\"></td>
	  <td style="width: 10px; height: {MESSAGE_HEIGHT}px; ">
	  </td>
	  <td style="text-align: center; vertical-align: middle;"><font color=\"!COLOR!\">&nbsp;&nbsp;!TEXT!</font></td>
	</tr>
  </tbody>
</table>
"""

ICON_NAME_TEMPLATE = f"""
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="width: {MESSAGE_ICON_SPACE_WIDTH}px; height: {MESSAGE_HEIGHT}px; text-align: center; vertical-align: middle;"><img src=\"!ICON!\" height=\"{MESSAGE_ICON_WIDTH}\" width=\"{MESSAGE_ICON_HEIGHT}\">&nbsp;</td>
	  <td style="width: 150px; height: {MESSAGE_HEIGHT}px; text-align: center; vertical-align: middle;"><font color=\"!COLOR!\">&nbsp;!USER!</font></td>
	  </td>
	  <td style="text-align: center; vertical-align: middle;"><font color=\"!COLOR!\">&nbsp;&nbsp;!TEXT!</font></td>
	</tr>
  </tbody>
</table>
"""

CHAT_TEMPLATE = f"""
<table style="width: 100%;" border="0">
  <tbody>
	<tr>
	  <td style="width: {MESSAGE_ICON_SPACE_WIDTH}px; height: {MESSAGE_HEIGHT}px; text-align: center; vertical-align: middle;">&nbsp;</td>
	  <td style="width: 150px; height: {MESSAGE_HEIGHT}px; text-align: center; vertical-align: middle;"><font color=\"!COLOR!\">!USER!</font>&nbsp;&nbsp;</td>
	  <td style="text-align: center; vertical-align: middle;">!TEXT!</td>
	</tr>
  </tbody>
</table>
"""

# ===========
# | CLASSES |
# ===========

class AboutDialog(QDialog):
	
	def __init__(self,parent=None):
		super(AboutDialog,self).__init__(parent)

		self.setWindowTitle(f"About {APPLICATION}")
		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		logo = QLabel()
		pixmap = QPixmap(QUIRC_LOGO_FILE)
		logo.setPixmap(pixmap)

		napp = QLabel(f"Version {VERSION}")
		napp.setAlignment(Qt.AlignCenter)
		napp.setFont(QUIRC_FONT)

		dapp = QLabel(f"{DESCRIPTION}")
		dapp.setAlignment(Qt.AlignCenter)
		dapp.setFont(QUIRC_FONT)

		uapp = QLabel("<a href=\"https://github.com/danhetrick/quirc\">https://github.com/danhetrick/quirc</a>")
		uapp.setAlignment(Qt.AlignCenter)
		uapp.setFont(QUIRC_FONT)
		uapp.setOpenExternalLinks(True)

		aexit = QPushButton("Ok")
		aexit.setFont(QUIRC_FONT)
		aexit.clicked.connect(self.close)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(logo)
		finalLayout.addWidget(napp)
		finalLayout.addWidget(dapp)
		finalLayout.addWidget(uapp)
		finalLayout.addWidget(aexit)
		self.setLayout(finalLayout)

class HelpDialog(QDialog):
	global GUI
	global CLIENT

	def cmdChange(self):
		cmd = self.cmdDisplay.currentText()

		if cmd == "What is IRC?":
			self.helpDisplay.setText("")
			self.helpDisplay.setHtml("""
"Internet Relay Chat (IRC) is an application layer protocol that facilitates communication in the form of text. The chat process works on a client/server networking model. IRC clients are computer programs that users can install on their system or web based applications running either locally in the browser or on 3rd party server. These clients communicate with chat servers to transfer messages to other clients. IRC is mainly designed for group communication in discussion forums, called channels, but also allows one-on-one communication via private messages..."
<br><br><i>--Wikipedia</i><br>
<i>https://en.wikipedia.org/wiki/Internet_Relay_Chat</i>
				""")

		if cmd == "Color Key":
			self.helpDisplay.setText("")
			self.helpDisplay.append(f"Different types of messages are displayed in different colors, depending on what kind of message it is.<br>")

			self.helpDisplay.append(f"""
<table style="width: 100%;" border="0">
      <tbody>
        <tr>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2><font color=\"{PUBLIC_MESSAGE_COLOR}\">Public Messages</font></h2>
          This is the color of standard IRC chat messages.</td>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2>&nbsp;<font color=\"{PRIVATE_MESSAGE_COLOR}\">Private Messages</font></h2>
          This is the color of IRC private messages.</td>
        </tr>
        <tr>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2><font color=\"{NOTICE_MESSAGE_COLOR}\">Notice Messages</font></h2>
          This is the color of IRC notice messages.</td>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2>&nbsp;<font color=\"{ACTION_MESSAGE_COLOR}\">Action Messages</font></h2>
          This is the color of CTCP action messages.</td>
        </tr>
        <tr>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2><font color=\"{SYSTEM_MESSAGE_COLOR}\">System Messages</font></h2>
          This is the color <b>Quirc</b> uses to display system information.</td>
          <td style="text-align: center; vertical-align: middle; background-color: #EAECEE;"><h2><font color=\"{ERROR_MESSAGE_COLOR}\">Error Messages</font></h2>
          This is the color <b>Quirc</b> uses to display errors.<br></td>
        </tr>
      </tbody>
    </table>
				""")

		if cmd == "Introduction":
			self.helpDisplay.setText("")
			self.helpDisplay.setText(f"<h1>{APPLICATION} {VERSION} Help</h1>")
			self.helpDisplay.append(f"Thank you for using <b>{APPLICATION}</b>!")
			self.helpDisplay.append(f"Select a topic or command to read documentation about that topic or command.")
			self.helpDisplay.append("All commands begin with a back slash (<b>/</b>), and take one or more arguments. Optional arguments are contained in <b>[</b> and <b>]</b>.")

		if cmd == "/join":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/join</b> <i>CHANNEL [KEY]</i></h1>")
			self.helpDisplay.append("Joins a channel. If the command is issued with no arguments, a dialog window will open ask for the channel (and channel key, if needed) to join. The channel key is only needed if the channel has the +k mode enabled.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/join #quirc</b><br><b>/join #privatechannel ch4ngem3</b><br>")

		if cmd == "/part":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/part</b> <i>CHANNEL</i></h1>")
			self.helpDisplay.append("Leaves a channel on the IRC server.<br>")
			self.helpDisplay.append("<h2>Example:</h2> <b>/part #quirc</b><br>")

		if cmd == "/nick":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/nick</b> <i>NEW_NICKNAME</i></h1>")
			self.helpDisplay.append("Changes the user's nickname. All nicknames on a server are unique; if the chosen nickname is already taken, a random number is attached to the desired nickname, and that is set as the nickname.<br>")
			self.helpDisplay.append("<h2>Example:</h2> <b>/nick Alice509</b><br>")

		if cmd == "/me":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/me</b> <i>MESSAGE</i></h1>")
			self.helpDisplay.append("Sends a CTCP action message. These appear as action descriptions; for example, if your username was \"funnygal\", and you used the command \"/me eats an apple\", the message would appear to other IRC users as \"funnygal eats an apple\".<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/me waves at everyone</b><br><b>/me looks shocked!</b><br>")

		if cmd == "/msg":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/msg</b> <i>TARGET MESSAGE</i></h1>")
			self.helpDisplay.append("Sends a message to a user or channel.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/msg bob how are you doing?</b><br><b>/msg #quirc Hello, everyone!</b><br>")

		if cmd == "/notice":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/notice</b> <i>TARGET MESSAGE</i></h1>")
			self.helpDisplay.append("Sends a notice to a user or channel.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/notice alice We're in #quirc!</b><br><b>/notice #quirc Alice should be here soon.</b><br>")

		if cmd == "/quit":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/quit</b> <i>[MESSAGE]</i></h1>")
			self.helpDisplay.append("Disconnects from the IRC server, optionally sending a parting message.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/quit</b><br><b>/quit See ya later!</b><br>")

		if cmd == "/kick":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/kick</b> <i>CHANNEL USER [MESSAGE]</i></h1>")
			self.helpDisplay.append("Kicks a user from a channel, sending an optional message. Only channel operators can kick users from a channel.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/kick #quirc alice</b><br><b>/kick #quirc carol Go away until you can be nice.</b><br>")

		if cmd == "/topic":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/topic</b> <i>NEW_TOPIC</i></h1>")
			self.helpDisplay.append("Sets a channel's topic.<br>")
			self.helpDisplay.append("<h2>Example:</h2> <b>/topic This is the new channel topic!</b><br>")

		if cmd == "/whois":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/whois</b> <i>USER [SERVER]</i></h1>")
			self.helpDisplay.append("Requests data about a user from the IRC server.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/whois joe</b><br><b>/whois joe irc3.choopa.net</b><br>")

		if cmd == "/invite":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/invite</b> <i>USER [CHANNEL]</i></h1>")
			self.helpDisplay.append("Invites a user to a channel; if CHANNEL is omitted, an invitation to the current channel is sent. CHANNEL must be specified if the server text display is open.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/invite bob_bot</b><br><b>/invite alice #quirc</b><br>")

		if cmd == "/ison":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/ison</b> <i>USER [USER] [...]</i></h1>")
			self.helpDisplay.append("Checks if a user or users are online (connected to the IRC server).<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/ison bob_bot</b><br><b>/ison alice bob carol daniel</b><br>")

		if cmd == "/knock":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/knock</b> <i>CHANNEL [MESSAGE]</i></h1>")
			self.helpDisplay.append("Requests an invitation from the users of an invitation-only channel.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/knock #quirc</b><br><b>/knock #quirc Anybody home?</b><br>")

		if cmd == "/ping":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/ping</b> <i>USER</i></h1>")
			self.helpDisplay.append("Sends a CTCP ping to a user or server, reporting the time taken.<br>")
			self.helpDisplay.append("<h2>Example:</h2> <b>/ping bob_bot</b><br>")

		if cmd == "/raw":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/raw</b> <i>MESSAGE</i></h1>")
			self.helpDisplay.append("Sends a raw, unprocessed message to the server. Used for supporting message and command types not supported by default in Quirc.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/raw PRIVMSG #quirc Hello!</b><br><b>/raw MODE #quirc +o bob</b><br>")

		if cmd == "/connect":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/connect</b> <i>HOST[:PORT]</i></h1>")
			self.helpDisplay.append("Connects to an IRC server. If <i>PORT</i> is omitted, 6667 is assumed.<br>")
			self.helpDisplay.append("<h1><b>/connect</b> <i>HOST PORT</i></h1>")
			self.helpDisplay.append("Connects to an IRC server.<br>")
			self.helpDisplay.append("<h2>Examples:</h2> <b>/connect irc.efnet.org</b><br><b>/connect chat.freenode.net:6667</b><br><b>/connect servercentral.il.us.quakenet.org 6667</b><br>")

		if cmd == "/ssl":
			self.helpDisplay.setText("")
			self.helpDisplay.append("<h1><b>/ssl</b> <i>HOST PORT</i></h1>")
			self.helpDisplay.append("Connects to an IRC server via SSL.<br>")
			self.helpDisplay.append("<h2>Example:</h2> <b>/ssl chat.freenode.net 6697</b><br>")

		if cmd == "Automatic Connect":
			self.helpDisplay.setText("")
			self.helpDisplay.append("When connected to an IRC server, click on <b>Quirc->Automatic Connect->To current server on startup</b> to automatically connect to the same IRC server the next time you start <b>Quirc</b>.<br>")
			self.helpDisplay.append("To automatically re-join <i>all</i> the channels you're currently in next time you connect to a server, click on <b>Quirc->Automatic Connect->To current channel(s) on startup</b>.<br>")

		if cmd == "Customize":
			self.helpDisplay.setText("")
			self.helpDisplay.append("The <b>Settings</b> menu contains two ways to customize <b>Quirc</b>: <b>Colors</b> allows you to customize what colors are used, and <b>Font</b> allows you to change the font.<br>")
			self.helpDisplay.append("<b>Quirc</b> comes with the amazing <b>Fira Code</b> font by Nikita Prokopov.<br>https://github.com/tonsky/FiraCode<br>")

			fl = """
Copyright (c) 2014, Nikita Prokopov http://tonsky.me
with Reserved Font Name Fira Code.

Copyright (c) 2014, Mozilla Foundation https://mozilla.org/
with Reserved Font Name Fira Sans.

Copyright (c) 2014, Mozilla Foundation https://mozilla.org/
with Reserved Font Name Fira Mono.

Copyright (c) 2014, Telefonica S.A.

This Font Software is licensed under the SIL Open Font License, Version 1.1.
			"""
			self.helpDisplay.append(fl)

	def __init__(self,parent=None):
		super(HelpDialog,self).__init__(parent)

		self.setWindowTitle(f"Help")
		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		cmdsBox = QGroupBox("")

		self.cmdDisplay = QComboBox(self)
		self.cmdDisplay.setFont(QUIRC_FONT_BOLD)
		self.cmdDisplay.addItem("Introduction")
		self.cmdDisplay.addItem("What is IRC?")
		self.cmdDisplay.addItem("Color Key")
		self.cmdDisplay.addItem("Automatic Connect")
		self.cmdDisplay.addItem("Customize")
		self.cmdDisplay.addItem("/connect")
		self.cmdDisplay.addItem("/ssl")
		self.cmdDisplay.addItem("/join")
		self.cmdDisplay.addItem("/part")
		self.cmdDisplay.addItem("/nick")
		self.cmdDisplay.addItem("/me")
		self.cmdDisplay.addItem("/msg")
		self.cmdDisplay.addItem("/notice")
		self.cmdDisplay.addItem("/quit")
		self.cmdDisplay.addItem("/kick")
		self.cmdDisplay.addItem("/topic")
		self.cmdDisplay.addItem("/whois")
		self.cmdDisplay.addItem("/invite")
		self.cmdDisplay.addItem("/ison")
		self.cmdDisplay.addItem("/knock")
		self.cmdDisplay.addItem("/ping")
		self.cmdDisplay.addItem("/raw")
		self.cmdDisplay.activated.connect(self.cmdChange)


		self.helpDisplay = QTextBrowser(self)
		self.helpDisplay.setFont(QUIRC_FONT)

		self.helpDisplay.setText(f"<h1>{APPLICATION} {VERSION} Help</h1>")
		self.helpDisplay.append(f"Thank you for using <b>{APPLICATION}</b>!")
		self.helpDisplay.append(f"Select a topic or command to read documentation about that topic or command.")
		self.helpDisplay.append("All commands begin with a back slash (<b>/</b>), and take one or more arguments. Optional arguments are contained in <b>[</b> and <b>]</b>.")

		textWidth = 500
		textHeight = 400
		self.helpDisplay.setMinimumSize(textWidth, textHeight)
		self.helpDisplay.resize(textWidth, textHeight)

		cbLayout = QVBoxLayout()
		cbLayout.addWidget(self.cmdDisplay)
		cbLayout.addWidget(self.helpDisplay)

		cmdsBox.setLayout(cbLayout)


		self.exit = QPushButton("Exit Help")
		self.exit.setFont(QUIRC_FONT)

		self.exit.clicked.connect(self.close)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(cmdsBox)
		finalLayout.addWidget(self.exit)
		self.setLayout(finalLayout)

class BanUserDialog(QDialog):
	global GUI
	global CLIENT
	def __init__(self,target,hostmask,parent=None):
		super(BanUserDialog,self).__init__(parent)
		self.target = target
		self.setWindowTitle(f"{CHANNEL}")
		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		hostmaskLayout = QHBoxLayout()
		self.kd = QLabel("Hostmask")
		self.kd.setFont(QUIRC_FONT_BOLD)
		self.hostmask = QLineEdit()
		self.hostmask.setFont(QUIRC_FONT)
		self.hostmask.setText(hostmask)
		hostmaskLayout.addWidget(self.kd)
		hostmaskLayout.addWidget(self.hostmask)

		self.go = QPushButton(f"Ban {target}")
		self.go.setFont(QUIRC_FONT)
		self.canc = QPushButton("Cancel")
		self.canc.setFont(QUIRC_FONT)
		self.go.clicked.connect(self.use)
		self.canc.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addLayout(hostmaskLayout)
		layout.addWidget(self.go)
		layout.addWidget(self.canc)
		self.setLayout(layout)

	def use(self):
		if CLIENT_IS_CONNECTED:
			h = self.hostmask.text()
			if h == '':
				CLIENT.mode(CHANNEL,True,"b",user=f"{self.target}")
			else:
				CLIENT.mode(CHANNEL,True,"b",user=f"{self.target}!{self.hostmask.text()}")
		GUI.activateWindow()
		self.close()

class KickUserDialog(QDialog):
	global GUI
	global CLIENT
	def __init__(self,target,hostmask,parent=None):
		super(KickUserDialog,self).__init__(parent)
		self.target = target
		self.setWindowTitle(f"{CHANNEL}")
		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		reasonLayout = QHBoxLayout()
		self.kd = QLabel("Reason")
		self.kd.setFont(QUIRC_FONT_BOLD)
		self.reason = QLineEdit()
		self.reason.setFont(QUIRC_FONT)
		reasonLayout.addWidget(self.kd)
		reasonLayout.addWidget(self.reason)

		self.go = QPushButton(f"Kick {target}")
		self.go.setFont(QUIRC_FONT)
		self.canc = QPushButton("Cancel")
		self.canc.setFont(QUIRC_FONT)
		self.go.clicked.connect(self.use)
		self.canc.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addLayout(reasonLayout)
		layout.addWidget(self.go)
		layout.addWidget(self.canc)
		self.setLayout(layout)

	def use(self):
		reason = self.reason.text()
		if CLIENT_IS_CONNECTED:
			if reason != '' or not reason.isspace():
				CLIENT.kick(CHANNEL,self.target)
			else:
				CLIENT.kick(CHANNEL,self.target,reason=reason)
		GUI.activateWindow()
		self.close()

class SetColorsDialog(QDialog):
	global GUI
	global CLIENT

	def selectChatColor(self):
		global PUBLIC_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(PUBLIC_MESSAGE_COLOR))
		if color.isValid():
			PUBLIC_MESSAGE_COLOR = color.name()
			self.cd.setText(f"<font color=\"{PUBLIC_MESSAGE_COLOR}\">Chat Text</font>")

	def selectPrivateColor(self):
		global PRIVATE_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(PRIVATE_MESSAGE_COLOR))
		if color.isValid():
			PRIVATE_MESSAGE_COLOR = color.name()
			self.pd.setText(f"<font color=\"{PRIVATE_MESSAGE_COLOR}\">Private Message Text</font>")

	def selectSystemColor(self):
		global SYSTEM_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(SYSTEM_MESSAGE_COLOR))
		if color.isValid():
			SYSTEM_MESSAGE_COLOR = color.name()
			self.sd.setText(f"<font color=\"{SYSTEM_MESSAGE_COLOR}\">System Text</font>")

	def selectActionColor(self):
		global ACTION_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(ACTION_MESSAGE_COLOR))
		if color.isValid():
			ACTION_MESSAGE_COLOR = color.name()
			self.ad.setText(f"<font color=\"{ACTION_MESSAGE_COLOR}\">Action Text</font>")

	def selectNoticeColor(self):
		global NOTICE_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(NOTICE_MESSAGE_COLOR))
		if color.isValid():
			NOTICE_MESSAGE_COLOR = color.name()
			self.nd.setText(f"<font color=\"{NOTICE_MESSAGE_COLOR}\">Notice Text</font>")

	def selectbgColor(self):
		global BACKGROUND_COLOR
		color = QColorDialog.getColor(initial=QColor(BACKGROUND_COLOR))
		if color.isValid():
			BACKGROUND_COLOR = color.name()
			self.bgd.setText(f"<font color=\"{BACKGROUND_COLOR}\">Background Color</font>")
			GUI.chatDisplay.setStyleSheet(f"background-color: \"{BACKGROUND_COLOR}\";")


			# elf.chat_display.setStyleSheet("QTextBrowser { background-color: #000000; color: white }")


	def selectErrorColor(self):
		global ERROR_MESSAGE_COLOR
		color = QColorDialog.getColor(initial=QColor(ERROR_MESSAGE_COLOR))
		if color.isValid():
			ERROR_MESSAGE_COLOR = color.name()
			self.ed.setText(f"<font color=\"{ERROR_MESSAGE_COLOR}\">Error Text</font>")

	def __init__(self,parent=None):
		super(SetColorsDialog,self).__init__(parent)

		self.setWindowTitle("Set Colors")
		self.setWindowIcon(QIcon(COLOR_ICON_FILE))

		noticeLayout = QHBoxLayout()
		self.nd = QLabel("Notice Text")
		self.nd.setFont(QUIRC_FONT_BOLD)
		self.noticeSet = QPushButton("Select Color")
		self.noticeSet.setFont(QUIRC_FONT)
		self.noticeSet.clicked.connect(self.selectNoticeColor)
		noticeLayout.addWidget(self.nd)
		noticeLayout.addWidget(self.noticeSet)

		self.nd.setText(f"<font color=\"{NOTICE_MESSAGE_COLOR}\">Notice Messages&nbsp;</font>")

		actionLayout = QHBoxLayout()
		self.ad = QLabel("Action Text")
		self.ad.setFont(QUIRC_FONT_BOLD)
		self.actionSet = QPushButton("Select Color")
		self.actionSet.setFont(QUIRC_FONT)
		self.actionSet.clicked.connect(self.selectActionColor)
		actionLayout.addWidget(self.ad)
		actionLayout.addWidget(self.actionSet)

		self.ad.setText(f"<font color=\"{ACTION_MESSAGE_COLOR}\">Action Messages&nbsp;</font>")

		chatLayout = QHBoxLayout()
		self.cd = QLabel("Chat Text")
		self.cd.setFont(QUIRC_FONT_BOLD)
		self.chatSet = QPushButton("Select Color")
		self.chatSet.setFont(QUIRC_FONT)
		self.chatSet.clicked.connect(self.selectChatColor)
		chatLayout.addWidget(self.cd)
		chatLayout.addWidget(self.chatSet)

		self.cd.setText(f"<font color=\"{PUBLIC_MESSAGE_COLOR}\">Public Messages&nbsp;</font>")

		privateLayout = QHBoxLayout()
		self.pd = QLabel("Private Messages")
		self.pd.setFont(QUIRC_FONT_BOLD)
		self.privateSet = QPushButton("Select Color")
		self.privateSet.setFont(QUIRC_FONT)
		self.privateSet.clicked.connect(self.selectPrivateColor)
		privateLayout.addWidget(self.pd)
		privateLayout.addWidget(self.privateSet)

		self.pd.setText(f"<font color=\"{PRIVATE_MESSAGE_COLOR}\">Private Messages</font>")

		systemLayout = QHBoxLayout()
		self.sd = QLabel("System Text")
		self.sd.setFont(QUIRC_FONT_BOLD)
		self.systemSet = QPushButton("Select Color")
		self.systemSet.setFont(QUIRC_FONT)
		self.systemSet.clicked.connect(self.selectSystemColor)
		systemLayout.addWidget(self.sd)
		systemLayout.addWidget(self.systemSet)

		self.sd.setText(f"<font color=\"{SYSTEM_MESSAGE_COLOR}\">System Text&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font>")



		errorLayout = QHBoxLayout()
		self.ed = QLabel("Error Text")
		self.ed.setFont(QUIRC_FONT_BOLD)
		self.errorSet = QPushButton("Select Color")
		self.errorSet.setFont(QUIRC_FONT)
		self.errorSet.clicked.connect(self.selectErrorColor)
		errorLayout.addWidget(self.ed)
		errorLayout.addWidget(self.errorSet)

		self.ed.setText(f"<font color=\"{ERROR_MESSAGE_COLOR}\">Error Text&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</font>")




		bgLayout = QHBoxLayout()
		self.bgd = QLabel("Background")
		self.bgd.setFont(QUIRC_FONT_BOLD)
		self.bgSet = QPushButton("Select Color")
		self.bgSet.setFont(QUIRC_FONT)
		self.bgSet.clicked.connect(self.selectbgColor)
		bgLayout.addWidget(self.bgd)
		bgLayout.addWidget(self.bgSet)

		self.bgd.setText(f"<font color=\"{BACKGROUND_COLOR}\">Background Color</font>")


		self.saveColor = QPushButton("Save")
		self.saveColor.setFont(QUIRC_FONT)
		self.saveColor.clicked.connect(self.saveColorToFile)

		self.cancelColor = QPushButton("Cancel")
		self.cancelColor.setFont(QUIRC_FONT)
		self.cancelColor.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addLayout(chatLayout)
		layout.addLayout(privateLayout)
		layout.addLayout(actionLayout)
		layout.addLayout(noticeLayout)
		layout.addLayout(systemLayout)
		layout.addLayout(errorLayout)
		layout.addLayout(bgLayout)
		layout.addWidget(self.saveColor)
		layout.addWidget(self.cancelColor)

		self.setLayout(layout)

	def saveColorToFile(self):
		cf = {
			"system": SYSTEM_MESSAGE_COLOR,
			"public": PUBLIC_MESSAGE_COLOR,
			"private": PRIVATE_MESSAGE_COLOR,
			"notice": NOTICE_MESSAGE_COLOR,
			"action": ACTION_MESSAGE_COLOR,
			"background": BACKGROUND_COLOR,
			"error": ERROR_MESSAGE_COLOR
		}
		with open(COLOR_INFORMATION_FILE, "w") as write_data:
			json.dump(cf, write_data)

		GUI.activateWindow()
		self.close()

class ServerConnectDialog(QDialog):
	global GUI
	global CLIENT

	def doConnect(self):

		global NICKNAME
		global USERNAME
		global REALNAME
		global CONNECT_ON_JOIN_CHANNEL
		global CONNECT_ON_JOIN_CHANNEL_KEY
		global SERVER_PASSWORD

		NICKNAME = self.nick.text()
		USERNAME = self.username.text()
		REALNAME = self.realname.text()

		if self.chan.text() != '':
			CONNECT_ON_JOIN_CHANNEL = self.chan.text()

		if self.key.text() != '':
			CONNECT_ON_JOIN_CHANNEL_KEY = self.key.text()

		# stored server
		if self.usePre.isChecked():
			p = int(self.sport.text())
			connect_to_irc(self.StoredServer,p)
			GUI.activateWindow()
			self.close()

		# custom server
		if self.useCustom.isChecked():
			s = self.cserv.text()
			p = int(self.cport.text())
			SERVER_PASSWORD = self.password.text()
			if self.DIALOG_CONNECT_VIA_SSL:
				ssl_to_irc(s,p)
			else:
				connect_to_irc(s,p)
			GUI.activateWindow()
			self.close()

	def setServer(self):
		self.StoredServer = self.servers.currentText()

	def clickSSL(self,state):
		if state == Qt.Checked:
			self.DIALOG_CONNECT_VIA_SSL = True
		else:
			self.DIALOG_CONNECT_VIA_SSL = False

	def toggle(self):
		if self.usePre.isChecked():
			# stored
			self.servers.setEnabled(True)
			self.sport.setEnabled(True)
			# custom
			self.cserv.setEnabled(False)
			self.cport.setEnabled(False)
			self.password.setEnabled(False)
			if IS_SSL_AVAILABLE: self.ssl.setEnabled(False)
		if self.useCustom.isChecked():
			# stored
			self.servers.setEnabled(False)
			self.sport.setEnabled(False)
			# custom
			self.cserv.setEnabled(True)
			self.cport.setEnabled(True)
			self.password.setEnabled(True)
			if IS_SSL_AVAILABLE: self.ssl.setEnabled(True)

	def __init__(self,parent=None):
		super(ServerConnectDialog,self).__init__(parent)
		#QUIRC_FONT_BOLD = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE, QFont.Bold)
		self.setWindowTitle("Connect to IRC")
		self.StoredServer = ''
		self.DIALOG_CONNECT_VIA_SSL = False

		self.setWindowTitle("Connect")
		self.setWindowIcon(QIcon(CONNECT_ICON_FILE))

		# User Settings Box

		userBox = QGroupBox("User Settings")
		userBox.setFont(QUIRC_FONT)

		nickLayout = QHBoxLayout()
		self.nd = QLabel("Nickname")
		self.nd.setFont(QUIRC_FONT_BOLD)
		self.nick = QLineEdit(f"{NICKNAME}")
		self.nick.setFont(QUIRC_FONT)
		nickLayout.addWidget(self.nd)
		nickLayout.addWidget(self.nick)

		realLayout = QHBoxLayout()
		self.rd = QLabel("IRC Name")
		self.rd.setFont(QUIRC_FONT_BOLD)
		self.realname = QLineEdit(f"{REALNAME}")
		self.realname.setFont(QUIRC_FONT)
		realLayout.addWidget(self.rd)
		realLayout.addWidget(self.realname)

		userLayout = QHBoxLayout()
		self.ud = QLabel("Username")
		self.ud.setFont(QUIRC_FONT_BOLD)
		self.username = QLineEdit(f"{USERNAME}")
		self.username.setFont(QUIRC_FONT)
		userLayout.addWidget(self.ud)
		userLayout.addWidget(self.username)

		ublayout = QVBoxLayout()
		ublayout.addLayout(nickLayout)
		ublayout.addLayout(realLayout)
		ublayout.addLayout(userLayout)

		userBox.setLayout(ublayout)

		# Channel Box

		channelBox = QGroupBox("Join Channel on Connect")
		channelBox.setFont(QUIRC_FONT)

		chanLayout = QHBoxLayout()
		self.cd = QLabel("Channel Name")
		self.cd.setFont(QUIRC_FONT_BOLD)
		self.chan = QLineEdit()
		self.chan.setFont(QUIRC_FONT)
		chanLayout.addWidget(self.cd)
		chanLayout.addWidget(self.chan)

		keyLayout = QHBoxLayout()
		self.kd = QLabel("Channel Key ")
		self.kd.setFont(QUIRC_FONT_BOLD)
		self.key = QLineEdit()
		self.key.setFont(QUIRC_FONT)
		keyLayout.addWidget(self.kd)
		keyLayout.addWidget(self.key)

		jclayout = QVBoxLayout()
		jclayout.addLayout(chanLayout)
		jclayout.addLayout(keyLayout)

		channelBox.setLayout(jclayout)

		# Select Server Type

		selectBox = QGroupBox("Connect to Server")
		selectBox.setFont(QUIRC_FONT)

		tselectLayout = QHBoxLayout()
		self.usePre = QRadioButton("Pre-set server")
		self.usePre.setFont(QUIRC_FONT)
		self.useCustom = QRadioButton("Enter server manually")
		self.useCustom.setFont(QUIRC_FONT)
		tselectLayout.addWidget(self.usePre)
		tselectLayout.addWidget(self.useCustom)
		self.usePre.setChecked(True)

		self.usePre.toggled.connect(self.toggle)
		
		selectBox.setLayout(tselectLayout)

		# Stored Server Box

		storedBox = QGroupBox("Pre-set Servers")
		storedBox.setFont(QUIRC_FONT)

		servLayout = QHBoxLayout()
		self.sd = QLabel("Server")
		self.sd.setFont(QUIRC_FONT_BOLD)
		self.servers = QComboBox(self)
		self.servers.setFont(QUIRC_FONT)
		self.servers.activated.connect(self.setServer)
		script = open(SERVER_LIST_FILE,"r")
		script = sorted(script, key=str.lower)
		for line in script:
			line = line.strip()
			self.servers.addItem(line)
		servLayout.addWidget(self.sd)
		servLayout.addWidget(self.servers)
		self.StoredServer = self.servers.currentText()

		sportLayout = QHBoxLayout()
		self.spd = QLabel("Port  ")
		self.spd.setFont(QUIRC_FONT_BOLD)
		self.sport = QLineEdit("6667")
		self.sport.setFont(QUIRC_FONT)
		sportLayout.addWidget(self.spd)
		sportLayout.addWidget(self.sport)

		ssblayout = QVBoxLayout()
		ssblayout.addLayout(servLayout)
		ssblayout.addLayout(sportLayout)

		storedBox.setLayout(ssblayout)

		# Custom Server Box

		customBox = QGroupBox("Manual Server Connection")
		customBox.setFont(QUIRC_FONT)

		cservLayout = QHBoxLayout()
		self.cpd = QLabel("Server  ")
		self.cpd.setFont(QUIRC_FONT_BOLD)
		self.cserv = QLineEdit()
		self.cserv.setFont(QUIRC_FONT)
		cservLayout.addWidget(self.cpd)
		cservLayout.addWidget(self.cserv)

		cpLayput = QHBoxLayout()
		self.csd = QLabel("Port    ")
		self.csd.setFont(QUIRC_FONT_BOLD)
		self.cport = QLineEdit()
		self.cport.setFont(QUIRC_FONT)
		cpLayput.addWidget(self.csd)
		cpLayput.addWidget(self.cport)

		pcpLayput = QHBoxLayout()
		self.pcsd = QLabel("Password")
		self.pcsd.setFont(QUIRC_FONT_BOLD)
		self.password = QLineEdit()
		self.password.setFont(QUIRC_FONT)
		pcpLayput.addWidget(self.pcsd)
		pcpLayput.addWidget(self.password)

		if IS_SSL_AVAILABLE:
			self.ssl = QCheckBox("Connect via SSL",self)
			self.ssl.setFont(QUIRC_FONT)
			self.ssl.stateChanged.connect(self.clickSSL)

		cslayout = QVBoxLayout()
		cslayout.addLayout(cservLayout)
		cslayout.addLayout(cpLayput)
		cslayout.addLayout(pcpLayput)
		if IS_SSL_AVAILABLE: cslayout.addWidget(self.ssl)

		customBox.setLayout(cslayout)

		# RIGHT

		rightLayout = QVBoxLayout()
		rightLayout.addWidget(selectBox)
		rightLayout.addWidget(storedBox)
		rightLayout.addWidget(customBox)

		leftLayout = QVBoxLayout()
		leftLayout.addWidget(userBox)
		leftLayout.addWidget(channelBox)

		totalLayout = QHBoxLayout()
		totalLayout.addLayout(leftLayout)
		totalLayout.addLayout(rightLayout)

		# Buttons

		buttonLayout = QHBoxLayout()

		self.connect = QPushButton("Connect")
		self.connect.setFont(QUIRC_FONT)
		self.cancel = QPushButton("Cancel")
		self.cancel.setFont(QUIRC_FONT)

		buttonLayout.addWidget(self.connect)
		buttonLayout.addWidget(self.cancel)

		self.cancel.clicked.connect(self.close)
		self.connect.clicked.connect(self.doConnect)

		# ALL WIDGETS

		finalLayout = QVBoxLayout()
		#finalLayout.addLayout(rightLayout)
		finalLayout.addLayout(totalLayout)
		finalLayout.addLayout(buttonLayout)

		self.cserv.setEnabled(False)
		self.cport.setEnabled(False)
		self.password.setEnabled(False)
		if IS_SSL_AVAILABLE: self.ssl.setEnabled(False)

		self.setLayout(finalLayout)

	def closeEvent(self, event):
		pass


class JoinChannelDialog(QDialog):
	global GUI
	global CLIENT
	def __init__(self,parent=None):
		super(JoinChannelDialog,self).__init__(parent)
		#QUIRC_FONT_BOLD = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE, QFont.Bold)
		self.setWindowTitle("Join Channel")
		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		chanLayout = QHBoxLayout()
		self.cd = QLabel("Channel Name")
		self.cd.setFont(QUIRC_FONT_BOLD)
		self.chan = QLineEdit()
		self.chan.setFont(QUIRC_FONT)
		chanLayout.addWidget(self.cd)
		chanLayout.addWidget(self.chan)

		keyLayout = QHBoxLayout()
		self.kd = QLabel("Channel Key ")
		self.kd.setFont(QUIRC_FONT_BOLD)
		self.key = QLineEdit()
		self.key.setFont(QUIRC_FONT)
		keyLayout.addWidget(self.kd)
		keyLayout.addWidget(self.key)

		self.go = QPushButton("Join")
		self.go.setFont(QUIRC_FONT)
		self.canc = QPushButton("Cancel")
		self.canc.setFont(QUIRC_FONT)
		self.go.clicked.connect(self.use)
		self.canc.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addLayout(chanLayout)
		layout.addLayout(keyLayout)
		layout.addWidget(self.go)
		layout.addWidget(self.canc)
		self.setLayout(layout)

	def use(self):
		channel = self.chan.text()
		key = self.key.text()
		if CLIENT_IS_CONNECTED:
			if key != '' or not key.isspace():
				CLIENT.join(channel,key)
			else:
				CLIENT.join(channel)
		GUI.activateWindow()
		self.close()

class SetUserInfo(QDialog):
	global GUI
	def __init__(self,parent=None):
		super(SetUserInfo,self).__init__(parent)
		#QUIRC_FONT_BOLD = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE, QFont.Bold)
		global NICKNAME
		global REALNAME
		global USERNAME
		self.setWindowTitle("User Settings")
		self.setWindowIcon(QIcon(USER_ICON_FILE))

		nickLayout = QHBoxLayout()
		self.nd = QLabel("Nickname")
		self.nd.setFont(QUIRC_FONT_BOLD)
		self.nick = QLineEdit(f"{NICKNAME}")
		self.nick.setFont(QUIRC_FONT)
		nickLayout.addWidget(self.nd)
		nickLayout.addWidget(self.nick)

		realLayout = QHBoxLayout()
		self.rd = QLabel("IRC Name")
		self.rd.setFont(QUIRC_FONT_BOLD)
		self.realname = QLineEdit(f"{REALNAME}")
		self.realname.setFont(QUIRC_FONT)
		realLayout.addWidget(self.rd)
		realLayout.addWidget(self.realname)

		userLayout = QHBoxLayout()
		self.ud = QLabel("Username")
		self.ud.setFont(QUIRC_FONT_BOLD)
		self.username = QLineEdit(f"{USERNAME}")
		self.username.setFont(QUIRC_FONT)
		userLayout.addWidget(self.ud)
		userLayout.addWidget(self.username)

		self.go = QPushButton("Use")
		self.go.setFont(QUIRC_FONT)
		self.sav = QPushButton("Use and Save as Default")
		self.sav.setFont(QUIRC_FONT)
		self.canc = QPushButton("Cancel")
		self.canc.setFont(QUIRC_FONT)
		self.go.clicked.connect(self.use)
		self.sav.clicked.connect(self.save)
		self.canc.clicked.connect(self.close)

		layout = QVBoxLayout()
		layout.addLayout(nickLayout)
		layout.addLayout(realLayout)
		layout.addLayout(userLayout)

		layout.addWidget(self.go)
		layout.addWidget(self.sav)
		layout.addWidget(self.canc)
		self.setLayout(layout)

	def save(self):
		global NICKNAME
		global REALNAME
		global USERNAME
		NICKNAME = self.nick.text()
		REALNAME = self.realname.text()
		USERNAME = self.username.text()
		data = [ NICKNAME, REALNAME, USERNAME ]
		with open(USER_INFORMATION_FILE, "w") as write_data:
			json.dump(data, write_data)
		GUI.activateWindow()
		self.close()

	def use(self):
		global NICKNAME
		global REALNAME
		global USERNAME
		NICKNAME = self.nick.text()
		REALNAME = self.realname.text()
		USERNAME = self.username.text()
		GUI.activateWindow()
		self.close()

class qpIRC_GUI(QMainWindow):

	def __init__(self,parent=None):
		super(qpIRC_GUI,self).__init__(parent)
		self.createUI()

		global GUI
		GUI = self

	def resizeEvent(self,resizeEvent):
		global CHANNEL
		window_width = self.width()
		window_height = self.height()

		base_x = 3
		base_y = 45

		cdisplay_height = window_height - 76
		cdisplay_width = window_width - 160
		ulist_width = 150
		ulist_height = cdisplay_height
		input_width = cdisplay_width + 3 + ulist_width
		input_height = 25
		chanlist_width = 150
		connect_b_width = 80

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.channelList.setGeometry(QtCore.QRect(base_x + cdisplay_width + 3, base_y , chanlist_width, input_height))
		self.userList.setGeometry(QtCore.QRect(base_x + cdisplay_width + 3, base_y + 25 + 3, ulist_width, ulist_height - 25 - 3))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width() + self.userList.width() + 3, input_height))
		self.statusDisplay.setGeometry(QtCore.QRect(base_x + 5, 18, window_width - base_x - 10, 30))

	def addChannel(self,data):
		if data.isspace(): return
		for i in range(self.channelList.count()):
			if self.channelList.itemText(i) == data:
				return
		self.channelList.addItem(data)

	def emptyChannel(self):
		self.channelList.clear()

	def removeChannel( self, text ):
		for i in range(self.channelList.count()):
			if self.channelList.itemText(i) == text:
				self.channelList.removeItem(i)

	def focusChannel( self, text ):
		for i in range(self.channelList.count()):
			if self.channelList.itemText(i) == text:
				self.channelList.setCurrentIndex(i)
				return

	def status(self,text):
		if text:
			self.statusDisplay.setText(f"{text}")

	def clearStatus(self):
		self.statusDisplay.setText("")

	def writeText(self,text):
		self.chatDisplay.append(text)
		self.chatDisplay.moveCursor(QTextCursor.End)

	def writeHtml(self,text):
		self.chatDisplay.insertHtml(f"{text}")
		self.chatDisplay.moveCursor(QTextCursor.End)

	def displayLastLine(self):
		self.chatDisplay.moveCursor(QTextCursor.End)

	def addUser(self,text):
		p = text.split('!')
		if len(p)==2:
			nick = p[0]
			host = p[1]
			items = self.userList.findItems(nick,Qt.MatchExactly)
			if len(items) > 0:
				return
			e = QListWidgetItem(nick)
			e.setToolTip(host)
			self.userList.addItem(e)
		else:
			items = self.userList.findItems(text,Qt.MatchExactly)
			if len(items) > 0:
				return
			self.userList.addItem(text)

	def removeUser( self, text ):
		items = self.userList.findItems(text,Qt.MatchExactly)
		if len(items) > 0:
			for item in items:
				self.userList.takeItem(self.userList.row(item))

	def emptyUsers(self):
		self.userList.clear()

	def getUsers(self):
		items = []
		ulist = []
		for index in range(self.userList.count()):
			items.append(self.userList.item(index))
		for item in items:
			ulist.append(item.text())
		return ulist

	def setUserInput(self,text):
		self.ircInput.setText(text)

	def manageUserInput(self):
		txt = self.ircInput.text()
		self.ircInput.setText('')

		if USER_INPUT_HISTORY_POINTER == 0:
			USER_INPUT_HISTORY.insert(1, txt)
		if len(USER_INPUT_HISTORY) > USER_INPUT_HISTORY_MAX_SIZE:
			USER_INPUT_HISTORY.pop()

		handleInput(txt)

	def keyPressEvent(self,event):
		global USER_INPUT_HISTORY
		global USER_INPUT_HISTORY_MAX_SIZE
		global USER_INPUT_HISTORY_POINTER
		if event.key() == Qt.Key_Up:
			USER_INPUT_HISTORY_POINTER = USER_INPUT_HISTORY_POINTER + 1
			if USER_INPUT_HISTORY_POINTER > USER_INPUT_HISTORY_MAX_SIZE: USER_INPUT_HISTORY_POINTER = USER_INPUT_HISTORY_MAX_SIZE
			if USER_INPUT_HISTORY_POINTER > (len(USER_INPUT_HISTORY)-1): USER_INPUT_HISTORY_POINTER = len(USER_INPUT_HISTORY) - 1
			self.ircInput.setText(USER_INPUT_HISTORY[USER_INPUT_HISTORY_POINTER])
		if event.key() == Qt.Key_Down:
			USER_INPUT_HISTORY_POINTER = USER_INPUT_HISTORY_POINTER - 1
			if USER_INPUT_HISTORY_POINTER <= 0: USER_INPUT_HISTORY_POINTER = 0
			self.ircInput.setText(USER_INPUT_HISTORY[USER_INPUT_HISTORY_POINTER])

	def menuConnect(self):
		c = ServerConnectDialog(parent=self)
		c.show()

	def menuJoin(self):
		c = JoinChannelDialog(parent=self)
		c.show()

	def menuHelpCommand(self):
		x = HelpDialog(parent=GUI)
		x.show()

	def menuDisconnect(self):
		CLIENT.quit()

	def menuAway(self):
		global CLIENT_IS_AWAY
		if CLIENT_IS_AWAY:
			CLIENT.back()
			CLIENT_IS_AWAY = False
			self.awayAct.setText("Set client as away")
			display_message('SYSTEM','','',"Client has been set to \"back\"",1)
		else:
			CLIENT.away()
			CLIENT_IS_AWAY = True
			self.awayAct.setText("Set client as back")
			display_message('SYSTEM','','',"Client has been set to \"away\"",1)

	def menuUser(self):
		c = SetUserInfo(parent=self)
		c.show()

	def menuAuto(self):
		if CONNECTED_VIA_SSL:
			data = [ 'ssl', SERVER, PORT, SERVER_PASSWORD ]
		else:
			data = [ 'normal', SERVER, PORT, SERVER_PASSWORD ]
		with open(SERVER_INFORMATION_FILE, "w") as write_data:
			json.dump(data, write_data)

	def menuColor(self):
		x = SetColorsDialog(parent=self)
		x.show()

	def menuFont(self):
		global QUIRC_FONT_BOLD
		global QUIRC_FONT

		f, ok = QFontDialog(parent=self).getFont(QUIRC_FONT)
		if ok:
			QUIRC_FONT = f
			QUIRC_FONT_BOLD = f
			QUIRC_FONT_BOLD.setBold(True)

		self.statusDisplay.setFont(QUIRC_FONT_BOLD)
		self.chatDisplay.setFont(QUIRC_FONT)
		self.userList.setFont(QUIRC_FONT_BOLD)
		self.channelList.setFont(QUIRC_FONT_BOLD)
		self.ircInput.setFont(QUIRC_FONT)

		saveFont()

	def menu1459Command(self):
		QDesktopServices.openUrl(QUrl("https://tools.ietf.org/html/rfc1459"))

	def menu2812Command(self):
		QDesktopServices.openUrl(QUrl("https://tools.ietf.org/html/rfc2812"))

	def menuAbout(self):
		x = AboutDialog(parent=self)
		x.show()

	def createUI(self):

		menubar = self.menuBar()

		menubar.setNativeMenuBar(False)

		serverMenu = menubar.addMenu("Quirc")

		self.connectAct = QAction(QIcon(CONNECT_ICON_FILE),"Connect to server",self)
		self.connectAct.triggered.connect(self.menuConnect)
		serverMenu.addAction(self.connectAct)

		self.disconnectAct = QAction(QIcon(CONNECT_ICON_FILE),"Disconnect from server",self)
		self.disconnectAct.triggered.connect(self.menuDisconnect)
		self.disconnectAct.setVisible(False)
		serverMenu.addAction(self.disconnectAct)

		serverMenu.addSeparator()

		autoconMenu = serverMenu.addMenu(QIcon(AUTO_ICON_FILE),"Automatic Connect")

		self.autoAct = QAction(QIcon(BOOKMARK_ICON_FILE),"To current server on startup",self)
		self.autoAct.triggered.connect(self.menuAuto)
		self.autoAct.setEnabled(False)
		autoconMenu.addAction(self.autoAct)

		self.ajoinAct = QAction(QIcon(BOOKMARK_ICON_FILE),"To current channel(s) on startup",self)
		self.ajoinAct.triggered.connect(self.menuAutoJoin)
		self.ajoinAct.setEnabled(False)
		autoconMenu.addAction(self.ajoinAct)

		serverMenu.addSeparator()

		self.joinAct = QAction(QIcon(IRC_ICON_FILE),"Join a channel",self)
		self.joinAct.triggered.connect(self.menuJoin)
		self.joinAct.setEnabled(False)
		serverMenu.addAction(self.joinAct)

		self.awayAct = QAction(QIcon(IRC_ICON_FILE),"Set client as away",self)
		self.awayAct.triggered.connect(self.menuAway)
		self.awayAct.setEnabled(False)
		serverMenu.addAction(self.awayAct)

		serverMenu.addSeparator()

		exitAct = QAction(QIcon(EXIT_ICON_FILE),"Exit",self)
		exitAct.triggered.connect(app.quit)
		serverMenu.addAction(exitAct)

		settingsMenu = menubar.addMenu("Settings")

		userAct = QAction(QIcon(USER_ICON_FILE),"User settings",self)
		userAct.triggered.connect(self.menuUser)
		settingsMenu.addAction(userAct)

		colorAct = QAction(QIcon(COLOR_ICON_FILE),"Colors",self)
		colorAct.triggered.connect(self.menuColor)
		settingsMenu.addAction(colorAct)


		fontAct = QAction(QIcon(FONT_ICON_FILE),"Font",self)
		fontAct.triggered.connect(self.menuFont)
		settingsMenu.addAction(fontAct)

		helpMenu = menubar.addMenu("Help")

		aboutHelpAct = QAction(QIcon(QUIRC_ICON_FILE),"About",self)
		aboutHelpAct.triggered.connect(self.menuAbout)
		helpMenu.addAction(aboutHelpAct)

		commandHelpAct = QAction(QIcon(SYSTEM_ICON_FILE),"Documentation",self)
		commandHelpAct.triggered.connect(self.menuHelpCommand)
		helpMenu.addAction(commandHelpAct)

		helpMenu.addSeparator()

		rfcMenu = helpMenu.addMenu(QIcon(FILE_ICON_FILE),"IRC Protocol")

		rfc1459HelpAct = QAction(QIcon(WEB_ICON_FILE),"RFC 1459",self)
		rfc1459HelpAct.triggered.connect(self.menu1459Command)
		rfcMenu.addAction(rfc1459HelpAct)

		rfc2812HelpAct = QAction(QIcon(WEB_ICON_FILE),"RFC 2812",self)
		rfc2812HelpAct.triggered.connect(self.menu2812Command)
		rfcMenu.addAction(rfc2812HelpAct)


		self.setWindowTitle(f"{APPLICATION}")

		self.setWindowIcon(QIcon(QUIRC_ICON_FILE))

		# Status display
		self.statusDisplay = QLabel(self)
		self.statusDisplay.setText("")
		self.statusDisplay.move(10,0)
		self.statusDisplay.setFont(QUIRC_FONT_BOLD)
		self.statusDisplay.setGeometry(QtCore.QRect(self.statusDisplay.x(), self.statusDisplay.y(), 615, 30))

		# Chat and input display
		self.chatDisplay = QTextBrowser(self)
		self.chatDisplay.setGeometry(QtCore.QRect(10, 10, 450, 425))
		self.chatDisplay.setFont(QUIRC_FONT)
		self.chatDisplay.setObjectName("chatDisplay")

		self.chatDisplay.anchorClicked.connect(self.linkClicked)

		sp = [DATA_DIRECTORY,INSTALL_DIRECTORY]
		self.chatDisplay.setSearchPaths(sp)

		# Channel user / Server channel display
		self.userList = QListWidget(self)
		self.userList.setGeometry(QtCore.QRect(self.chatDisplay.width()+15, 10, 150, 425))
		self.userList.setFont(QUIRC_FONT_BOLD)
		self.userList.setObjectName("userList")
		self.userList.itemDoubleClicked.connect(self.userClicked)
		self.userList.installEventFilter(self)

		# Channel list display
		self.channelList = QComboBox(self)
		self.channelList.setGeometry(3,self.chatDisplay.height()+15,50,25)
		self.channelList.setFont(QUIRC_FONT)
		self.channelList.activated.connect(self.channelChange)

		# User input
		self.ircInput = QLineEdit(self)
		self.ircInput.setGeometry(QtCore.QRect(10, self.chatDisplay.height()+15, 605, 30))
		self.ircInput.setFont(QUIRC_FONT)
		self.ircInput.setObjectName("ircInput")
		self.ircInput.returnPressed.connect(self.manageUserInput)

		self.setGeometry(QtCore.QRect(10, 10, 640, 480))

		self.center()
		self.show()

	def menuAutoJoin(self):
		cl = getChannelList()
		with open(CHANNEL_INFORMATION_FILE, "w") as write_data:
			json.dump(cl, write_data)

	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			txt = self.chatDisplay.toHtml()
			QDesktopServices.openUrl(url)
			self.chatDisplay.setText(txt)

	def eventFilter(self, source, event):
		global CLIENT
		
		if (event.type() == QtCore.QEvent.ContextMenu and source is self.userList and CHANNEL != '' and CLIENT_IS_CONNECTED):
			item = source.itemAt(event.pos())
			if item is None: return True

			hostmask = item.toolTip()

			menu = QMenu()
			msgAct = menu.addAction(QIcon(CHAT_ICON_FILE),'Send message')
			noticeAct = menu.addAction(QIcon(CHAT_ICON_FILE),'Send notice')
			menu.addSeparator()
			whoisAct = menu.addAction(QIcon(WHOIS_ICON_FILE),'WHOIS user')
			if CLIENT_IS_CHANNEL_OPERATOR:
				kickAct = menu.addAction(QIcon(KICK_ICON_FILE),'Kick User')
				banAct = menu.addAction(QIcon(BAN_ICON_FILE),'Ban User')

			menu.addSeparator()
			urlAct = menu.addAction(QIcon(CLIPBOARD_ICON_FILE),'Copy channel URL to clipboard')
			topicAct = menu.addAction(QIcon(CLIPBOARD_ICON_FILE),'Copy channel topic to clipboard')
			copyAct = menu.addAction(QIcon(CLIPBOARD_ICON_FILE),'Copy user list to clipboard')

			action = menu.exec_(self.userList.mapToGlobal(event.pos()))

			target = item.text()
			if '@' in target:
				TARGET_IS_OP = True
			else:
				TARGET_IS_OP = False
			if '+' in target:
				TARGET_IS_VOICED = True
			else:
				TARGET_IS_VOICED = False
			target = target.replace("@","")
			target = target.replace("+","")

			if CLIENT_IS_CHANNEL_OPERATOR:
				if action == banAct:
					x = BanUserDialog(target,hostmask,parent=self)
					x.show()

				if action == kickAct:
					x = KickUserDialog(target,hostmask,parent=self)
					x.show()

			if action == msgAct:
				self.ircInput.setText(f"/msg {target} ")
				self.ircInput.setFocus()
				return True

			if action == noticeAct:
				self.ircInput.setText(f"/notice {target} ")
				self.ircInput.setFocus()
				return True

			if action == whoisAct:
				CLIENT.whois(target)
				return True

			if action == urlAct:
				cc = CHANNEL.replace('#','')
				iu = f"irc://{SERVER}:{PORT}/{cc}"
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText(iu, mode=cb.Clipboard)
				return True

			if action == copyAct:
				ulist = self.getUsers()
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText("\n".join(ulist), mode=cb.Clipboard)
				return True

			if action == topicAct:
				t = getTopic(CHANNEL)
				cb = QApplication.clipboard()
				cb.clear(mode=cb.Clipboard )
				cb.setText(t, mode=cb.Clipboard)
				return True

		return super(qpIRC_GUI, self).eventFilter(source, event)

	def userClicked(self):
		c = self.userList.currentItem().text()
		userDoubleClicked(c)

	def clearChat(self):
		self.chatDisplay.clear()

	def channelChange(self):
		chan = self.channelList.currentText()
		changedChannel(chan)

	def closeEvent(self, event):
		app.quit()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

class qpIRC_ClientConnection(irc.IRCClient):

	global GUI
	global NICKNAME
	global REALNAME
	global USERNAME

	nickname = NICKNAME
	realname = REALNAME
	username = USERNAME

	def __init__(self):
		self.beep = 1

	def pong(self, user, secs):
		p = user.split('!')
		if len(p) == 2:
			pnick = p[0]
			phostmask = p[1]
		else:
			pnick = user
			phostmask = user
		secs = round(secs,8)
		display_message('SYSTEM','','',f"Ping reply from {pnick}: {secs} seconds",1)

		return irc.IRCClient.pong(self, user, secs)

	def register(self,nickname,hostname='foo',servername='bar'):
		if SERVER_PASSWORD != '':
			self.password = SERVER_PASSWORD
		if self.password is not None:
			self.sendLine("PASS %s" % self.password)
		self.setNick(NICKNAME)
		self.username = USERNAME
		self.realname = REALNAME
		self.nickname = NICKNAME
		self.sendLine("USER %s %s %s :%s" % (USERNAME, hostname, servername, REALNAME))

		GUI.connectAct.setVisible(False)
		GUI.disconnectAct.setText(f"Disconnect from {SERVER}:{PORT}")
		GUI.disconnectAct.setVisible(True)
		GUI.joinAct.setEnabled(True)
		GUI.awayAct.setEnabled(True)
		GUI.autoAct.setEnabled(True)
		GUI.ajoinAct.setEnabled(True)

		return irc.IRCClient.register(self,nickname,hostname='foo',servername='bar')

	def connectionMade(self):
		global CLIENT_IS_CONNECTED
		global SERVER
		global PORT
		global CLIENT_IS_AWAY
		CLIENT_IS_CONNECTED = True
		CLIENT_IS_AWAY = False
		display_message('SYSTEM','','',f"Connected to {SERVER}:{PORT}",1)
		updateTopic()
		moveInitializeTextToServerChat()
		return irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):
		global CLIENT_IS_CONNECTED
		global SERVER
		global PORT
		global CHANNEL
		global CLIENT_IS_AWAY
		global CHANNEL_DATABASE
		global SERVER_PAGE_BUFFER
		CLIENT_IS_CONNECTED = False 
		changedChannel(SERVER)
		nc = []
		for c in CHANNEL_DATABASE:
			if c.Channel == SERVER:
				c.Channel == ''
				nc.append(c)
		CHANNEL_DATABASE = nc
		GUI.emptyChannel()
		GUI.emptyUsers()
		GUI.clearStatus()
		display_message('SYSTEM','','',f"Connection to {SERVER}:{PORT} lost",1)
		CHANNEL = ''
		SERVER = ''
		PORT = ''
		GUI.connectAct.setVisible(True)
		GUI.disconnectAct.setText("Disconnect from server")
		GUI.disconnectAct.setVisible(False)
		GUI.joinAct.setEnabled(False)
		GUI.awayAct.setEnabled(False)
		GUI.autoAct.setEnabled(False)
		GUI.ajoinAct.setEnabled(False)
		if CLIENT_IS_AWAY:
			CLIENT_IS_AWAY = False
			GUI.awayAct.setText("Set client as away")

		return irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		global AUTO_JOIN
		display_message('SYSTEM','','',"Registered!",1)
		GUI.addChannel(SERVER)
		if LOADED_USER_INFO_FROM_FILE:
			CLIENT.setNick(NICKNAME)
		global CONNECT_ON_JOIN_CHANNEL
		global CONNECT_ON_JOIN_CHANNEL_KEY
		if CONNECT_ON_JOIN_CHANNEL != '':
			if CONNECT_ON_JOIN_CHANNEL_KEY != '':
				self.join(CONNECT_ON_JOIN_CHANNEL,key=CONNECT_ON_JOIN_CHANNEL_KEY)
				CONNECT_ON_JOIN_CHANNEL = ''
				CONNECT_ON_JOIN_CHANNEL_KEY = ''
			else:
				self.join(CONNECT_ON_JOIN_CHANNEL)
				CONNECT_ON_JOIN_CHANNEL = ''
		# Auto-join channels
		for c in AUTO_JOIN:
			CLIENT.join(c)
		AUTO_JOIN = []
		# request full NAMES format
		self.sendLine("PROTOCTL UHNAMES")


	def joined(self, channel):
		global CHANNEL
		global GUI
		global SERVER
		CHANNEL = channel
		GUI.addChannel(channel)
		CLIENT_IS_CHANNEL_OPERATOR = False
		refreshUserlist()
		updateTopic()
		GUI.focusChannel(channel)
		changedChannel(channel)
		display_message('SYSTEM','','',f"Joined {channel}",1)

	def privmsg(self, user, target, msg):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]

		if SCRUB_HTML_FROM_INCOMING_MESSAGES: msg = scrub_html(msg)
		if TURN_URLS_INTO_LINKS: msg = format_links(msg)

		if target != self.nickname:
			# public message
			display_message('PUBLIC',target,pnick,msg,1)
		else:
			# private message
			display_message('PRIVATE',target,pnick,msg,1)

	def noticed(self, user, channel, message):
		global CHANNEL
		tokens = user.split('!')
		if len(tokens) >= 2:
			pnick = tokens[0]
			phostmask = tokens[1]
		else:
			pnick = user
			phostmask = user

		if SCRUB_HTML_FROM_INCOMING_MESSAGES: message = scrub_html(message)
		if TURN_URLS_INTO_LINKS: message = format_links(message)

		display_message('NOTICE',channel,pnick,message,1)

	def receivedMOTD(self, motd):
		for line in motd:
			if SCRUB_HTML_FROM_INCOMING_MESSAGES: line = scrub_html(line)
			if TURN_URLS_INTO_LINKS: line = format_links(line)
			display_message('SYSTEM','','',line,1)

	def userJoined(self, user, channel):
		display_message('JOIN',channel,user,f"{user} joined {channel}",1)
		refreshUserlist()

	def userLeft(self, user, channel):
		display_message('PART',channel,user,f"{user} left {channel}",1)
		refreshUserlist()

	def irc_ERR_NICKNAMEINUSE(self, prefix, params):
		global NICKNAME
		oldNick = NICKNAME
		NICKNAME = f"{NICKNAME}{random.randint(100, 999)}"
		self.setNick(NICKNAME)
		display_message('SYSTEM','','',f"Nick collision! Nickname changed to {NICKNAME}",1)
		refreshUserlist()

	def userRenamed(self, oldname, newname):
		display_message('SYSTEM','','',f"{oldname} is now known as {newname}",1)
		refreshUserlist()

	def topicUpdated(self, user, channel, newTopic):
		display_message('TOPIC',channel,user,f"{user} changed the topic to {newTopic}",1)
		storeTopic(channel,newTopic)
		updateTopic()

	def action(self, user, channel, data):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]

		if SCRUB_HTML_FROM_INCOMING_MESSAGES: data = scrub_html(data)
		if TURN_URLS_INTO_LINKS: data = format_links(data)

		display_message('ACTION',channel,pnick,data,1)

	def userKicked(self, kickee, channel, kicker, message):
		if len(message)>0:
			display_message('KICK',channel,kicker,f"{kicker} kicked {kickee} from {channel}: {message}",1)
		else:
			display_message('KICK',channel,kicker,f"{kicker} kicked {kickee} from {channel}",1)
		refreshUserlist()

	def kickedFrom(self, channel, kicker, message):
		if len(message)>0:
			display_message('SYSTEM',channel,kicker,f"{kicker} kicked you from {channel}: {message}",1)
		else:
			display_message('SYSTEM',channel,kicker,f"{kicker} kicked you from {channel}",1)

	def irc_RPL_TOPIC(self, prefix, params):
		global TOPIC
		channel = params[1]
		if not params[2].isspace():
			display_message('TOPIC',channel,'',f"{channel} topic is \"{params[2]}\"",1)
			storeTopic(channel,params[2])
			updateTopic()
		else:
			storeTopic(channel,'')
			updateTopic()

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
				display_message('SYSTEM','','',f"{nick} quit IRC ({msg})",1)
			else:
				display_message('SYSTEM','','',f"{nick} quit IRC",1)
		refreshUserlist()

	def modeChanged(self, user, channel, set, modes, args):

		p = user.split('!')
		if len(p) == 2:
			pnick = user.split('!')[0]
			phostmask = user.split('!')[1]
		else:
			pnick = user
			phostmask = user
		text = ''
		if 'o' in modes:
			if set:
				for u in args:
					# u + operator
					text = f"{pnick} made {u} a {channel} channel operator"
			else:
				for u in args:
					# u - operator
					text = f"{pnick} removed channel operator status from {u}"
		if 'v' in modes:
			if set:
				for u in args:
					# u + voiced
					text = f"{pnick} set {u}'s status to \"voiced\""
			else:
				for u in args:
					# u - voiced
					text = f"{pnick} set {u}'s status to \"unvoiced\""
		if 'p' in modes:
			if set:
				# channel status private
				text = f"{pnick} set {channel} to private"
			else:
				# channel public
				text = f"{pnick} set {channel} to public"
		if 'k' in modes:
			if len(args) >= 1:
				nkey = args[0]
			else:
				nkey = ''
			if set:
				# nkey = channel key
				text = f"{pnick} set {channel}'s key to {nkey}"
			else:
				# removed channel key
				text = f"{pnick} removed {channel}'s key"

		if len(text) == 0:
			if set:
				if len(modes) > 1:
					text = f"{pnick} set modes +{''.join(modes)} on {channel}"
				else:
					text = f"{pnick} set mode +{''.join(modes)} on {channel}"
			else:
				if len(modes) > 1:
					text = f"{pnick} set modes -{''.join(modes)} on {channel}"
				else:
					text = f"{pnick} set mode -{''.join(modes)} on {channel}"
		refreshUserlist()
		display_message('MODE',channel,user,text,1)

	def irc_RPL_NAMREPLY(self, prefix, params):
		global CHANNEL_USER_LIST
		channel = params[2].lower()
		nicklist = params[3].split(' ')
		for nick in nicklist:
			CHANNEL_USER_LIST.append(nick)

	def irc_RPL_ENDOFNAMES(self, prefix, params):
		global CHANNEL_USER_LIST
		global GUI
		global CLIENT_IS_CHANNEL_OPERATOR
		ulist = sortNicks(CHANNEL_USER_LIST)
		GUI.emptyUsers()
		for nick in ulist:
			if len(nick) == 0: continue
			p = nick.split('!')
			if len(p)==2:
				if p[0] == f"@{NICKNAME}":
					CLIENT_IS_CHANNEL_OPERATOR = True
			GUI.addUser(nick)

	def irc_RPL_WHOISCHANNELS(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		channels = ", ".join(params)
		display_message('SYSTEM','','',f"{nick} is in {channels}",1)

	def irc_RPL_WHOISUSER(self, prefix, params):
		nick = params[1]
		username = params[2]
		host = params[3]
		realname = params[5]
		display_message('SYSTEM','','',f"{nick}({username})'s host is {host}",1)

	def irc_RPL_WHOISIDLE(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		idle_time = params.pop(0)
		signed_on = params.pop(0)

		idle_time = str(timedelta(seconds=(int(idle_time))))
		signed_on = datetime.fromtimestamp(int(signed_on)).strftime("%A, %B %d, %Y %I:%M:%S")
		display_message('SYSTEM','','',f"{nick} connected on {signed_on}",1)
		display_message('SYSTEM','','',f"{nick} has been idle for {idle_time}",1)

	def irc_RPL_WHOISSERVER(self, prefix, params):
		nick = params[1]
		server = params[2]
		display_message('SYSTEM','','',f"{nick} is connected to {server}",1)

	def irc_RPL_ENDOFWHOIS(self, prefix, params):
		nick = params[1]
		display_message('SYSTEM','','',f"End of whois data for {nick}",1)

	def irc_RPL_ISON(self, prefix, params):
		uonline = params[1]
		uonline.strip()
		if len(uonline) == 0:
			display_message('SYSTEM','','',f"Online users not found",1)
		else:
			display_message('SYSTEM','','',f"Online users: {uonline}",1)

	def lineReceived(self, line):
		try:
			line2 = line.decode('UTF-8')
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		d = line2.split(" ",1)
		if len(d) >= 2:
			if d[1].isalpha(): return irc.IRCClient.lineReceived(self, line)
		if "Cannot join channel (+k)" in line2:
			display_message('ERROR','','',"Cannot join channel (wrong or missing password)",1)
		if "Cannot join channel (+l)" in line2:
			display_message('ERROR','','',"Cannot join channel (channel is full)",1)
		if "Cannot join channel (+b)" in line2:
			display_message('ERROR','','',"Cannot join channel (banned)",1)
		if "Cannot join channel (+i)" in line2:
			display_message('ERROR','','',"Cannot join channel (channel is invite only)",1)
		if "not an IRC operator" in line2:
			display_message('ERROR','','',"Permission denied (you're not an IRC operator",1)
		if "not channel operator" in line2:
			display_message('ERROR','','',"Permission denied (you're not channel operator)",1)
		if "is already on channel" in line2:
			display_message('ERROR','','',"Invite failed (user is already in channel)",1)
		if "not on that channel" in line2:
			display_message('ERROR','','',"Permission denied (you're not in channel)",1)
		if "aren't on that channel" in line2:
			display_message('ERROR','','',"Permission denied (target user is not in channel)",1)
		if "have not registered" in line2:
			display_message('ERROR','','',"You're not registered",1)
		if "may not reregister" in line2:
			display_message('ERROR','','',"You can't reregister",1)
		if "enough parameters" in line2:
			display_message('ERROR','','',"Error: not enough parameters supplied to command",1)
		if "isn't among the privileged" in line2:
			display_message('ERROR','','',"Registration refused (server isn't setup to allow connections from your host)",1)
		if "Password incorrect" in line2:
			display_message('ERROR','','',"Permission denied (incorrect password)",1)
		if "banned from this server" in line2:
			display_message('ERROR','','',"You are banned from this server",1)
		if "kill a server" in line2:
			display_message('ERROR','','',"Permission denied (you can't kill a server)",1)
		if "O-lines for your host" in line2:
			display_message('ERROR','','',"Error: no O-lines for your host",1)
		if "Unknown MODE flag" in line2:
			display_message('ERROR','','',"Error: unknown MODE flag",1)
		if "change mode for other users" in line2:
			display_message('ERROR','','',"Permission denied (can't change mode for other users)",1)
		return irc.IRCClient.lineReceived(self, line)



class qpIRC_ConnectionFactory(protocol.ClientFactory):
	def __init__(self):
		self.config = 0

	def buildProtocol(self, addr):
		global CLIENT
		CLIENT = qpIRC_ClientConnection()
		CLIENT.factory = self
		return CLIENT

	def clientConnectionLost(self, connector, reason):
		pass

	def clientConnectionFailed(self, connector, reason):
		pass

# ===============
# | SUBROUTINES |
# ===============

def scrub_html(txt):
	clean = re.compile('<.*?>')
	return re.sub(clean, '', txt)

def format_links(txt):
	urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', txt)

	for u in urls:
		link = f"<b><i><a href=\"{u}\">{u}</a></i></b>"
		txt = txt.replace(u,link)
	return txt

def userDoubleClicked(item):
	if CHANNEL == '':
		changedChannel(item)
	else:
		global GUI
		t = item.replace('@','')
		t = t.replace('+','')
		GUI.setUserInput(f"/msg {t} ")

def changedChannel(channel):
	global GUI
	global CHANNEL
	global CLIENT_IS_CHANNEL_OPERATOR
	CLIENT_IS_CHANNEL_OPERATOR = False
	GUI.clearChat()
	GUI.focusChannel(channel)
	if channel == SERVER:
		CHANNEL = ''
	else:
		CHANNEL = channel
	updateTopic()
	if channel != SERVER: refreshUserlist()
	for c in getChat(channel):
		display_message(c.Type,c.Channel,c.User,c.Message,0)
	if channel == SERVER:
		GUI.emptyUsers()
		cl = getChannelList()
		if len(cl) >= 1:
			for c in cl:
				GUI.addUser(c)
		else:
			GUI.addUser("No channels")

def getChannelList():
	rc = []
	for c in CHANNEL_DATABASE:
		if c.Channel != SERVER: rc.append(c.Channel)
	return list(set(rc))

def ssl_to_irc(host,port):
	global CLIENT
	global CLIENT_IS_CONNECTED
	global SERVER
	global PORT
	global CONNECTED_VIA_SSL
	global CONNECTED_ONCE

	if CLIENT_IS_CONNECTED:
		CLIENT.quit()
		CLIENT_IS_CONNECTED = False

	SERVER = host
	PORT = int(port)

	CONNECTED_VIA_SSL = True

	CLIENT = qpIRC_ConnectionFactory()
	reactor.connectSSL(host, int(port), CLIENT, ssl.ClientContextFactory())

def connect_to_irc(host,port):
	global CLIENT
	global CLIENT_IS_CONNECTED
	global SERVER
	global PORT
	global CONNECTED_ONCE

	if CLIENT_IS_CONNECTED:
		CLIENT.quit()
		CLIENT_IS_CONNECTED = False

	SERVER = host
	PORT = int(port)

	CLIENT = qpIRC_ConnectionFactory()
	reactor.connectTCP(host, int(port), CLIENT)

def refreshUserlist():
	global CHANNEL_USER_LIST
	global CHANNEL
	global CLIENT
	if CHANNEL == '': return
	CHANNEL_USER_LIST = []
	CLIENT.sendLine(f"NAMES {CHANNEL}")

def handleCommands(text):
	global GUI
	global CLIENT
	global CHANNEL

	tokens = text.split()

	# |======|
	# | JOIN |
	# |======|

	if len(tokens) == 2:
		if tokens[0].lower() == '/join':
			chan = tokens[1]
			if CLIENT_IS_CONNECTED:
				CLIENT.join(chan)
			else:
				display_message('SYSTEM','','',"Can't join channel (not connected to a server)",1)
			return True

	if len(tokens) >= 3:
		if tokens[0].lower() == '/join':
			chan = tokens[1]
			key = tokens[2]
			if CLIENT_IS_CONNECTED:
				CLIENT.join(chan,key=key)
			else:
				display_message('SYSTEM','','',"Can't join channel (not connected to a server)",1)
			return True

	if len(tokens) == 1:
		if tokens[0].lower() == '/join':
			if CLIENT_IS_CONNECTED:
				c = JoinChannelDialog(parent=GUI)
				c.show()
			else:
				display_message('SYSTEM','','',"Can't join channel (not connected to a server)",1)
			return True

	# |======|
	# | PART |
	# |======|

	if len(tokens) == 2:
		if tokens[0].lower() == '/part':
			chan = tokens[1]
			if CLIENT_IS_CONNECTED:
				if chan in getChannelList():
					CLIENT.part(chan)
					GUI.removeChannel(chan)
					removeChat(chan)
					if CHANNEL == '':
						changedChannel(SERVER)
					if chan == CHANNEL:
						CHANNEL = ''
						changedChannel(SERVER)
				else:
					display_message('SYSTEM','','',f"Can't part channel (you're not in {chan})",1)
			else:
				display_message('SYSTEM','','',"Can't part channel (not connected to a server)",1)
			return True

	if len(tokens) != 2:
		if len(tokens)>=1 and tokens[0].lower() == '/part':
			display_message('SYSTEM','','',"USAGE: /part CHANNEL",1)
			return True


	# |======|
	# | NICK |
	# |======|

	if len(tokens) == 2:
		global NICKNAME
		if tokens[0].lower() == '/nick':
			newnick = tokens[1]
			if CLIENT_IS_CONNECTED:
				display_message('SYSTEM','','',f"Changing nickname from \"{NICKNAME}\" to \"{newnick}\"",1)
				NICKNAME = newnick
				CLIENT.setNick(newnick)
				refreshUserlist()
			else:
				display_message('ERROR','','',"Can't change nickname (not connected to a server)",1)
			return True

	if len(tokens) != 2:
		if len(tokens)>=1 and tokens[0].lower() == '/nick':
			display_message('SYSTEM','','',"USAGE: /nick NEW_NICKNAME",1)
			return True

	# |====|
	# | ME |
	# |====|

	if len(tokens) >= 2:
		if tokens[0].lower() == '/me':
			tokens.pop(0)
			msg = ' '.join(tokens)
			if CLIENT_IS_CONNECTED:
				if CHANNEL != '':
					CLIENT.msg(CHANNEL,f"\x01ACTION {msg}\x01")
					if TURN_URLS_INTO_LINKS: msg = format_links(msg)
					display_message('ACTION',CHANNEL,NICKNAME,msg,1)
			else:
				display_message('ERROR','','',"Can't send CTCP action message (not connected to a server)",1)
			return True

	if len(tokens) >= 1 and tokens[0].lower() == '/me':
		display_message('SYSTEM','','',"USAGE: /me ACTION",1)
		return True

	# |=====|
	# | MSG |
	# |=====|

	if len(tokens) >= 3:
		if tokens[0].lower() == '/msg':
			tokens.pop(0)
			target = tokens.pop(0)
			msg = ' '.join(tokens)
			if CLIENT_IS_CONNECTED:
				CLIENT.msg(target,msg)
				if TURN_URLS_INTO_LINKS: msg = format_links(msg)
				display_message('OUTPRIVATE',target,f"{NICKNAME}->{target}",msg,1)
			else:
				display_message('ERROR','','',"Can't send message (not connected to a server)",1)
			return True

	if len(tokens) >= 1 and tokens[0].lower() == '/msg':
		display_message('SYSTEM','','',"USAGE: /msg TARGET MESSAGE",1)
		return True

	# |========|
	# | NOTICE |
	# |========|

	if len(tokens) >= 3:
		if tokens[0].lower() == '/notice':
			tokens.pop(0)
			target = tokens.pop(0)
			msg = ' '.join(tokens)
			if CLIENT_IS_CONNECTED:
				CLIENT.notice(target,msg)
				if TURN_URLS_INTO_LINKS: msg = format_links(msg)
				display_message('OUTNOTICE',target,f"{NICKNAME}->{target}",msg,1)
			else:
				display_message('ERROR','','',"Can't send notice (not connected to a server)",1)
			return True

	if len(tokens) >= 1 and tokens[0].lower() == '/notice':
		display_message('SYSTEM','','',"USAGE: /notice TARGET MESSAGE",1)
		return True

	# |======|
	# | QUIT |
	# |======|

	if len(tokens) == 1 and tokens[0].lower() == '/quit':
		if CLIENT_IS_CONNECTED:
			CLIENT.quit()
		else:
			display_message('ERROR','','',"Can't quit (not connected to a server)",1)
		return True

	if len(tokens) > 1 and tokens[0].lower() == '/quit':
		tokens.pop(0)
		msg = ' '.join(tokens)
		CLIENT.quit(message=msg)
		return True

	# |======|
	# | KICK |
	# |======|
	
	if len(tokens) == 3 and tokens[0].lower() == '/kick':
		if CLIENT_IS_CONNECTED:
			chan = tokens[1]
			user = tokens[2]
			CLIENT.kick(chan,user)
		else:
			display_message('ERROR','','',"Can't kick user (not connected to a server)",1)
		return True

	if len(tokens) > 3 and tokens[0].lower() == '/kick':
		if CLIENT_IS_CONNECTED:
			tokens.pop(0)
			chan = tokens.pop(0)
			user = tokens.pop(0)
			msg = ' '.join(tokens)
			CLIENT.kick(chan,user,reason=msg)
		else:
			display_message('ERROR','','',"Can't kick user (not connected to a server)",1)
		return True

	if len(tokens) < 3 and tokens[0].lower() == '/kick':
		display_message('SYSTEM','','',"USAGE: /quit CHANNEL USER [MESSAGE]",1)
		return True

	# |=======|
	# | TOPIC |
	# |=======|
	
	if len(tokens) > 2 and tokens[0].lower() == '/topic':
		if CLIENT_IS_CONNECTED:
			tokens.pop(0)
			chan = tokens.pop(0)
			msg = ' '.join(tokens)
			CLIENT.topic(chan,topic=msg)
		else:
			display_message('ERROR','','',"Can't set channel topic (not connected to a server)",1)
		return True

	if len(tokens) < 2 and tokens[0].lower() == '/topic':
		display_message('SYSTEM','','',"USAGE: /topic CHANNEL NEW_TOPIC",1)
		return True

	if len(tokens) == 2 and tokens[0].lower() == '/topic':
		display_message('SYSTEM','','',"USAGE: /topic CHANNEL NEW_TOPIC",1)
		return True

	# |=======|
	# | WHOIS |
	# |=======|

	if len(tokens) == 2 and tokens[0].lower() == '/whois':
		if CLIENT_IS_CONNECTED:
			target = tokens[1]
			CLIENT.whois(target)
		else:
			display_message('ERROR','','',"Can't request WHOIS (not connected to a server)",1)
		return True

	if len(tokens) == 3 and tokens[0].lower() == '/whois':
		if CLIENT_IS_CONNECTED:
			target = tokens[1]
			serv = tokens[2]
			CLIENT.whois(target,server=serv)
		else:
			display_message('ERROR','','',"Can't request WHOIS (not connected to a server)",1)
		return True

	if len(tokens) > 3 and tokens[0].lower() == '/whois':
		display_message('SYSTEM','','',"USAGE: /whois USER [SERVER]",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/whois':
		display_message('SYSTEM','','',"USAGE: /whois USER [SERVER]",1)
		return True

	# |========|
	# | INVITE |
	# |========|

	if len(tokens) == 3 and tokens[0].lower() == '/invite':
		if CLIENT_IS_CONNECTED:
			user = tokens[1]
			chan = tokens[2]
			CLIENT.sendLine(f"INVITE {user} {chan}")
		else:
			display_message('ERROR','','',"Can't invite user (not connected to a server)",1)
		return True

	if len(tokens) == 2 and tokens[0].lower() == '/invite':
		if CLIENT_IS_CONNECTED:
			if CHANNEL == '':
				display_message('ERROR','','',"Channel must be specified",1)
				display_message('SYSTEM','','',"USAGE: /invite USER CHANNEL",1)
				return True
			user = tokens[1]
			CLIENT.sendLine(f"INVITE {user} {CHANNEL}")
		else:
			display_message('ERROR','','',"Can't invite user (not connected to a server)",1)
		return True

	if len(tokens) > 3 and tokens[0].lower() == '/invite':
		if CHANNEL != '':
			display_message('SYSTEM','','',"USAGE: /invite USER [CHANNEL]",1)
			display_message('SYSTEM','','',"If CHANNEL is omitted, an invitation to the current channel is sent",1)
		else:
			display_message('SYSTEM','','',"USAGE: /invite USER CHANNEL",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/invite':
		if CHANNEL != '':
			display_message('SYSTEM','','',"USAGE: /invite USER [CHANNEL]",1)
			display_message('SYSTEM','','',"If CHANNEL is omitted, an invitation to the current channel is sent",1)
		else:
			display_message('SYSTEM','','',"USAGE: /invite USER CHANNEL",1)
		return True

	# |======|
	# | ISON |
	# |======|

	if len(tokens) >= 2 and tokens[0].lower() == '/ison':
		if CLIENT_IS_CONNECTED:
			tokens.pop(0)
			users = ' '.join(tokens)
			CLIENT.sendLine(f"ISON {users}")
		else:
			display_message('ERROR','','',"Can't check user status (not connected to a server)",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/ison':
		display_message('SYSTEM','','',"USAGE: /ison USER [USER...]",1)
		return True

	# |=======|
	# | KNOCK |
	# |=======|

	if len(tokens) == 2 and tokens[0].lower() == '/knock':
		if CLIENT_IS_CONNECTED:
			chan = tokens[1]
			CLIENT.sendLine(f"KNOCK {chan}")
		else:
			display_message('ERROR','','',"Can't knock channel (not connected to a server)",1)
		return True

	if len(tokens) >= 3 and tokens[0].lower() == '/knock':
		if CLIENT_IS_CONNECTED:
			tokens.pop(0)
			chan = tokens.pop(0)
			msg = ' '.join(tokens)
			CLIENT.sendLine(f"KNOCK {chan} {msg}")
		else:
			display_message('ERROR','','',"Can't knock channel (not connected to a server)",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/knock':
		display_message('SYSTEM','','',"USAGE: /knock CHANNEL [MESSAGE]",1)
		return True

	# |=====|
	# | RAW |
	# |=====|

	if len(tokens) > 1 and tokens[0].lower() == '/raw':
		if CLIENT_IS_CONNECTED:
			tokens.pop(0)
			msg = ' '.join(tokens)
			CLIENT.sendLine(f"{msg}")
		else:
			display_message('ERROR','','',"Can't send raw message (not connected to a server)",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/raw':
		display_message('SYSTEM','','',"USAGE: /raw MESSAGE",1)
		return True

	# |======|
	# | PING |
	# |======|

	if len(tokens) == 2 and tokens[0].lower() == '/ping':
		if CLIENT_IS_CONNECTED:
			target = tokens[1]
			CLIENT.ping(target)
		else:
			display_message('ERROR','','',"Can't send ping (not connected to a server)",1)
		return True

	if len(tokens) == 1 and tokens[0].lower() == '/ping':
		display_message('SYSTEM','','',"USAGE: /ping USER",1)
		return True

	if len(tokens) > 2 and tokens[0].lower() == '/ping':
		display_message('SYSTEM','','',"USAGE: /ping USER",1)
		return True

	# |=========|
	# | CONNECT |
	# |=========|

	if len(tokens) == 2 and tokens[0].lower() == '/connect':
		target = tokens[1]
		x = target.split(':')
		if len(x)==2:
			serv = x[0]
			port = x[1]
			if port.isalpha():
				display_message('ERROR','','',f"Can't use {port} as a port number",1)
				return True
			connect_to_irc(serv,port)
		else:
			serv = target
			connect_to_irc(target,6667)
		return True

	if len(tokens) == 3 and tokens[0].lower() == '/connect':
		serv = tokens[1]
		port = tokens[2]
		if port.isalpha():
			display_message('ERROR','','',f"Can't use {port} as a port number",1)
			return True
		connect_to_irc(serv,port)
		return True

	if len(tokens) < 2 and tokens[0].lower() == '/connect':
		display_message('SYSTEM','','',"USAGE: /connect HOST[:PORT] (if PORT is omitted, 6667 is assumed) -or- /connect HOST PORT",1)
		return True

	if len(tokens) > 3 and tokens[0].lower() == '/connect':
		display_message('SYSTEM','','',"USAGE: /connect HOST[:PORT] (if PORT is omitted, 6667 is assumed) -or- /connect HOST PORT",1)
		return True

	# |=====|
	# | SSL |
	# |=====|

	if len(tokens) == 3 and tokens[0].lower() == '/ssl':
		serv = tokens[1]
		port = tokens[2]
		if port.isalpha():
			display_message('ERROR','','',f"Can't use {port} as a port number",1)
			return True
		ssl_to_irc(serv,port)
		return True

	if len(tokens) != 3 and tokens[0].lower() == '/ssl':
		display_message('SYSTEM','','',"USAGE: /ssl HOST PORT",1)
		return True


def handleInput(text):
	global GUI
	global CLIENT
	global CHANNEL

	USER_INPUT_HISTORY_POINTER = 0

	if len(text)>=1 and text[0] == '/':
		if not handleCommands(text):
			display_message('ERROR','','',f"Unrecognized command: {text}",1)
			return
		else:
			return

	if CHANNEL != '':
		CLIENT.msg(CHANNEL,text,length=MAXIMUM_IRC_MESSAGE_LENGTH)
		if TURN_URLS_INTO_LINKS: text = format_links(text)
		display_message('PUBLIC',CHANNEL,NICKNAME,text,1)

class Chat(object):
	def __init__(self,mtype,chan,user,msg):
		self.Type = mtype
		self.Channel = chan
		self.User = user
		self.Message = msg

class Topic(object):
	def __init__(self,channel,topic):
		self.Channel = channel
		self.Topic = topic

def updateTopic():
	global GUI
	global CHANNEL
	if CHANNEL == '':
		if CONNECTED_VIA_SSL:
			GUI.status(f"Connected to {SERVER}:{PORT} via SSL")
		else:
			GUI.status(f"Connected to {SERVER}:{PORT}")
	t = getTopic(CHANNEL)
	if t != '':
		GUI.status(f"{CHANNEL} - {t}")
	else:
		GUI.status(f"{CHANNEL}")

def getTopic(channel):
	global TOPIC_DATABASE
	for t in TOPIC_DATABASE:
		if t.Channel == channel: return t.Topic
	return ''

def storeTopic(channel,topic):
	global TOPIC_DATABASE
	nt = []
	found = False
	for t in TOPIC_DATABASE:
		if t.Channel == channel:
			t.Topic = topic
			found = True
		nt.append(t)
	if found:
		TOPIC_DATABASE = nt
		return
	t = Topic(channel,topic)
	TOPIC_DATABASE.append(t)

def moveInitializeTextToServerChat():
	global CHANNEL_DATABASE
	rc = []
	for c in CHANNEL_DATABASE:
		if c.Channel == '':
			c.Channel = SERVER
		rc.append(c)
	CHANNEL_DATABASE = rc

def getChat(channel):
	rc = []
	for c in CHANNEL_DATABASE:
		if c.Channel == channel:
			rc.append(c)
	return rc

def removeChat(channel):
	global CHANNEL_DATABASE
	rc = []
	for c in CHANNEL_DATABASE:
		if c.Channel != channel:
			rc.append(c)
	CHANNEL_DATABASE = rc

def storeChat(co):
	global CHANNEL_DATABASE
	global CHANNEL
	CHANNEL_DATABASE.append(co)

def pad_nick(nick,size):
	if len(nick) >= size: return nick
	x = size - len(nick)
	y = '&nbsp;'*x
	return f"{y}{nick}"

def display_message(mtype,channel,user,message,store):
	global GUI
	global CHAT_TEMPLATE
	global CHANNEL
	if mtype.lower() == 'public':
		padded_user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE + 1)
		response = CHAT_TEMPLATE.replace('!COLOR!',PUBLIC_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'private':
		response = ICON_NAME_TEMPLATE.replace('!COLOR!',PRIVATE_MESSAGE_COLOR)
		response = response.replace('!ICON!',PRIVATE_ICON)
		response = response.replace('!USER!',f"<b><u>{user}</u></b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'outprivate':
		response = ICON_NAME_TEMPLATE.replace('!COLOR!',PRIVATE_MESSAGE_COLOR)
		response = response.replace('!ICON!',PRIVATE_ICON)
		response = response.replace('!USER!',f"<b><u>{user}</u></b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'outnotice':
		response = ICON_NAME_TEMPLATE.replace('!COLOR!',NOTICE_MESSAGE_COLOR)
		response = response.replace('!ICON!',NOTICE_ICON)
		response = response.replace('!USER!',f"<b><u>{user}</u></b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'notice':
		response = ICON_NAME_TEMPLATE.replace('!COLOR!',NOTICE_MESSAGE_COLOR)
		response = response.replace('!ICON!',NOTICE_ICON)
		response = response.replace('!USER!',f"<b><u>{user}</u></b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'action':
		response = ICON_TEMPLATE.replace('!COLOR!',ACTION_MESSAGE_COLOR)
		response = response.replace('!ICON!',ACTION_ICON)
		response = response.replace('!TEXT!',f"<b>{user} {message}</b>")
	elif mtype.lower() == 'system':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',SYSTEM_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'join':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'part':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'topic':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'kick':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'mode':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'usermode':
		response = ICON_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!ICON!',IRC_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	elif mtype.lower() == 'ascii':
		response = f"<pre>{message}</pre>"
	elif mtype.lower() == 'raw':
		response = f"{message}"
	elif mtype.lower() == 'error':
		response = ICON_TEMPLATE.replace('!COLOR!',ERROR_MESSAGE_COLOR)
		response = response.replace('!ICON!',ERROR_ICON)
		response = response.replace('!TEXT!',f"<b>{message}</b>")
	else:
		return
	doPrint = True
	if mtype.lower() == 'topic' and channel != CHANNEL: doPrint = False
	if doPrint:
		GUI.writeText(response)
	if store == 1:

		if mtype.lower() == 'public' or mtype.lower() == 'action':
			m = Chat(mtype,CHANNEL,user,message)
			storeChat(m)
			return

		if mtype.lower() == 'private' or mtype.lower() == 'outprivate':
			if CHANNEL != '':
				m = Chat(mtype,CHANNEL,user,message)
				storeChat(m)
			m = Chat(mtype,SERVER,user,message)
			storeChat(m)
			return

		if mtype.lower() == 'notice' or mtype.lower() == 'outnotice':
			if CHANNEL != '':
				m = Chat(mtype,CHANNEL,user,message)
				storeChat(m)
			m = Chat(mtype,SERVER,user,message)
			storeChat(m)
			return

		if channel == '' or channel == NICKNAME or channel == '*':
			m = Chat(mtype,SERVER,user,message)
			storeChat(m)
			if CHANNEL != '':
				m = Chat(mtype,CHANNEL,user,message)
				storeChat(m)
		else:
			if len(channel)>=1:
				if channel[0] != '#':
					if channel[0] !='&': return
			m = Chat(mtype,channel,user,message)
			storeChat(m)

def sortNicks(nicklist):
	ops = []
	voiced = []
	normal = []
	sortnicks = []
	for nick in nicklist:
		if nick.isspace(): continue
		if '@' in nick:
			ops.append(nick)
		elif '+' in nick:
			voiced.append(nick)
		else:
			normal.append(nick)
	ops = sorted(ops, key=str.lower)
	voiced = sorted(voiced, key=str.lower)
	normal = sorted(normal, key=str.lower)
	for nick in ops:
		sortnicks.append(nick)
	for nick in voiced:
		sortnicks.append(nick)
	for nick in normal:
		sortnicks.append(nick)
	return sortnicks

def saveFont():
	with open(FONT_INFORMATION_FILE, "w") as write_data:
		json.dump(QUIRC_FONT.toString(), write_data)

def loadFont():
	if os.path.isfile(FONT_INFORMATION_FILE):
		with open(FONT_INFORMATION_FILE, "r") as read_font:
			global QUIRC_FONT
			global QUIRC_FONT_BOLD
			data = json.load(read_font)
			QUIRC_FONT = QFont()
			QUIRC_FONT.fromString(data)
			QUIRC_FONT_BOLD = QUIRC_FONT
			QUIRC_FONT_BOLD.setBold(True)

def displayBanner():
	banner = f"""<a href=\"https://github.com/danhetrick/quirc\">
<img src=\"{QUIRC_LOGO}\"></a><br>
<i>{DESCRIPTION}</i><br>
	"""

	display_message('RAW','','',f"{banner}",1)
	display_message('RAW','','',"Connect to IRC with the <b>/connect</b> or <b>/ssl</b> commands, or select a server from the <b>Quirc</b> menu by clicking on \"Connect to server\"!",1)

# ================
# | MAIN PROGRAM |
# ================

if __name__ == '__main__':

	# Load user information if present
	if os.path.isfile(USER_INFORMATION_FILE):
		with open(USER_INFORMATION_FILE, "r") as read_user:
			data = json.load(read_user)
			if len(data) != 3:
				print(f"User data in {USER_INFORMATION_FILE} is malformed")
			else:
				NICKNAME = data[0]
				REALNAME = data[1]
				USERNAME = data[2]
				LOADED_USER_INFO_FROM_FILE = True

	loadFont()

	# Spawn the GUI
	global GUI
	GUI = qpIRC_GUI()

	displayBanner()

	if os.path.isfile(COLOR_INFORMATION_FILE):
		with open(COLOR_INFORMATION_FILE, "r") as read_color:
			data = json.load(read_color)
			SYSTEM_MESSAGE_COLOR = data["system"]
			PUBLIC_MESSAGE_COLOR = data["public"]
			PRIVATE_MESSAGE_COLOR = data["private"]
			NOTICE_MESSAGE_COLOR = data["notice"]
			ACTION_MESSAGE_COLOR = data["action"]
			BACKGROUND_COLOR = data["background"]
			ERROR_MESSAGE_COLOR = data["error"]
			GUI.chatDisplay.setStyleSheet(f"background-color: \"{BACKGROUND_COLOR}\";")

	# Load user information if present
	if os.path.isfile(CHANNEL_INFORMATION_FILE):
		with open(CHANNEL_INFORMATION_FILE, "r") as read_chans:
			AUTO_JOIN = json.load(read_chans)

	# Load server information if present
	if os.path.isfile(SERVER_INFORMATION_FILE):
		with open(SERVER_INFORMATION_FILE, "r") as read_serv:
			data = json.load(read_serv)
			if len(data) != 4:
				display_message('ERROR','','',f"Server data in {SERVER_INFORMATION_FILE} is malformed",1)
			else:
				SERVER = data[1]
				PORT = int(data[2])
				SERVER_PASSWORD = data[3]
				if data[0].lower() == 'ssl':
					display_message('SYSTEM','','',f"Auto connecting to {SERVER}:{PORT} via SSL",1)
					ssl_to_irc(SERVER,PORT)
				else:
					display_message('SYSTEM','','',f"Auto connecting to {SERVER}:{PORT}",1)
					connect_to_irc(SERVER,PORT)

	reactor.run()
