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
VERSION = "0.02662"
DESCRIPTION = "A Python3/Qt5 IRC client"

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

MESSAGE_TEMPLATE = "<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\"><tr><td><font color=!COLOR!>&#9679;&nbsp;</font></td><td>&nbsp;&nbsp;<font color=!COLOR!>!TEXT!</font></td></tr></table>"
CHAT_TEMPLATE = "<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\"><tr><td>&nbsp;</td><td><font color=\"!COLOR!\">!USER!</font>&nbsp;&nbsp;</td><td>!TEXT!</td></tr></table>"
PRIVATE_TEMPLATE = "<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\"><tr><td><font color=!COLOR!>&#9679;&nbsp;</font></td><td><font color=\"!COLOR!\">!USER!</font>&nbsp;&nbsp;</td><td><font color=!COLOR!>!TEXT!</font></td></tr></table>"

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

USER_INFORMATION_FILE = os.path.join(INSTALL_DIRECTORY, "user.json")
SERVER_INFORMATION_FILE = os.path.join(INSTALL_DIRECTORY, "server.json")
COLOR_INFORMATION_FILE = os.path.join(INSTALL_DIRECTORY, "colors.json")

SERVER_LIST_FILE = os.path.join(DATA_DIRECTORY, "servers.txt")
COMMAND_HELP_FILE = os.path.join(DATA_DIRECTORY, "commands.txt")

IRC_ICON_FILE = os.path.join(DATA_DIRECTORY, "irc.png")
GEAR_ICON_FILE = os.path.join(DATA_DIRECTORY, "gear.png")
INFO_ICON_FILE = os.path.join(DATA_DIRECTORY, "info.png")
CONNECT_ICON_FILE = os.path.join(DATA_DIRECTORY, "connect.png")
USER_ICON_FILE = os.path.join(DATA_DIRECTORY, "user.png")
COLOR_ICON_FILE = os.path.join(DATA_DIRECTORY, "colors.png")
FONT_ICON_FILE = os.path.join(DATA_DIRECTORY, "font.png")
DISCONNECT_ICON_FILE = os.path.join(DATA_DIRECTORY, "disconnect.png")


QUIRC_FONT_BOLD = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE, QFont.Bold)
QUIRC_FONT = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE)


# ===========
# | CLASSES |
# ===========

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

	def __init__(self,parent=None):
		super(SetColorsDialog,self).__init__(parent)

		QUIRC_FONT_BOLD = QFont(DISPLAY_FONT, DISPLAY_FONT_SIZE, QFont.Bold)
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
			"background": BACKGROUND_COLOR
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
		self.setWindowIcon(QIcon(IRC_ICON_FILE))

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
		QDesktopServices.openUrl(QUrl(f"file:///{COMMAND_HELP_FILE}"))

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


	def createUI(self):

		menubar = self.menuBar()

		serverMenu = menubar.addMenu("Quirc")

		self.connectAct = QAction(QIcon(CONNECT_ICON_FILE),"Connect to server",self)
		self.connectAct.triggered.connect(self.menuConnect)
		serverMenu.addAction(self.connectAct)

		self.disconnectAct = QAction(QIcon(DISCONNECT_ICON_FILE),"Disconnect from server",self)
		self.disconnectAct.triggered.connect(self.menuDisconnect)
		self.disconnectAct.setEnabled(False)
		serverMenu.addAction(self.disconnectAct)

		serverMenu.addSeparator()

		self.joinAct = QAction("Join a channel",self)
		self.joinAct.triggered.connect(self.menuJoin)
		self.joinAct.setEnabled(False)
		serverMenu.addAction(self.joinAct)

		self.awayAct = QAction("Set client as away",self)
		self.awayAct.triggered.connect(self.menuAway)
		self.awayAct.setEnabled(False)
		serverMenu.addAction(self.awayAct)

		serverMenu.addSeparator()

		exitAct = QAction("Exit",self)
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

		self.autoAct = QAction(QIcon(CONNECT_ICON_FILE),"Auto-connect to current server",self)
		self.autoAct.triggered.connect(self.menuAuto)
		self.autoAct.setEnabled(False)
		settingsMenu.addAction(self.autoAct)

		helpMenu = menubar.addMenu("Help")

		commandHelpAct = QAction(QIcon(INFO_ICON_FILE),"Command documentation",self)
		commandHelpAct.triggered.connect(self.menuHelpCommand)
		helpMenu.addAction(commandHelpAct)


		self.setWindowTitle(f"{APPLICATION}")

		self.setWindowIcon(QIcon(IRC_ICON_FILE))

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
		self.channelList.setFont(QUIRC_FONT_BOLD)
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

			menu = QMenu()
			msgAct = menu.addAction('Send message')
			noticeAct = menu.addAction('Send notice')
			whoisAct = menu.addAction('WHOIS user')
			menu.addSeparator()
			urlAct = menu.addAction('Copy channel URL to clipboard')
			topicAct = menu.addAction('Copy channel topic to clipboard')
			copyAct = menu.addAction('Copy user list to clipboard')
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

		GUI.connectAct.setEnabled(False)
		GUI.disconnectAct.setText(f"Disconnect from {SERVER}:{PORT}")
		GUI.disconnectAct.setEnabled(True)
		GUI.joinAct.setEnabled(True)
		GUI.awayAct.setEnabled(True)
		GUI.autoAct.setEnabled(True)

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
		CLIENT_IS_CONNECTED = False
		changedChannel(SERVER)
		GUI.emptyChannel()
		GUI.emptyUsers()
		GUI.clearStatus()
		display_message('SYSTEM','','',f"Connection to {SERVER}:{PORT} lost",1)
		CHANNEL = ''
		SERVER = ''
		PORT = ''
		GUI.connectAct.setEnabled(True)
		GUI.disconnectAct.setText("Disconnect from server")
		GUI.disconnectAct.setEnabled(False)
		GUI.joinAct.setEnabled(False)
		GUI.awayAct.setEnabled(False)
		GUI.autoAct.setEnabled(False)
		if CLIENT_IS_AWAY:
			CLIENT_IS_AWAY = False
			GUI.awayAct.setText("Set client as away")

		return irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):
		display_message('SYSTEM','','',"Registered!",1)
		GUI.addChannel(SERVER)
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
					text = f"{pnick} gave ops to {u}"
			else:
				for u in args:
					# u - operator
					text = f"{pnick} took ops from {u}"
		if 'v' in modes:
			if set:
				for u in args:
					# u + voiced
					text = f"{pnick} gave voiced to {u}"
			else:
				for u in args:
					# u - voiced
					text = f"{pnick} took voiced from {u}"
		if 'p' in modes:
			if set:
				# channel status private
				text = f"{pnick} set channel mode to private"
			else:
				# channel public
				text = f"{pnick} set channel mode to public"
		if 'k' in modes:
			if len(args) >= 1:
				nkey = args[0]
			else:
				nkey = ''
			if set:
				# nkey = channel key
				text = f"{pnick} set channel key to {nkey}"
			else:
				# removed channel key
				text = f"{pnick} removed channel key"
		if channel == NICKNAME:
			if set:
				text = f"{pnick} set mode(s) +{''.join(modes)}"
			else:
				text = f"{pnick} set mode(s) -{''.join(modes)}"
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
			if nick == f"@{NICKNAME}":
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

	def lineReceived(self, line):
		try:
			line2 = line.decode('UTF-8')
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		d = line2.split(" ",1)
		if len(d) >= 2:
			if d[1].isalpha(): return irc.IRCClient.lineReceived(self, line)
		if "Cannot join channel (+k)" in line2:
			display_message('SYSTEM','','',"Cannot join channel (wrong or missing password)",1)
		if "Cannot join channel (+l)" in line2:
			display_message('SYSTEM','','',"Cannot join channel (channel is full)",1)
		if "Cannot join channel (+b)" in line2:
			display_message('SYSTEM','','',"Cannot join channel (banned)",1)
		if "Cannot join channel (+i)" in line2:
			display_message('SYSTEM','','',"Cannot join channel (channel is invite only)",1)
		if "not an IRC operator" in line2:
			display_message('SYSTEM','','',"Permission denied (you're not an IRC operator",1)
		if "not channel operator" in line2:
			display_message('SYSTEM','','',"Permission denied (you're not channel operator)",1)
		if "is already on channel" in line2:
			display_message('SYSTEM','','',"Invite failed (user is already in channel)",1)
		if "not on that channel" in line2:
			display_message('SYSTEM','','',"Permission denied (you're not in channel)",1)
		if "aren't on that channel" in line2:
			display_message('SYSTEM','','',"Permission denied (target user is not in channel)",1)
		if "have not registered" in line2:
			display_message('SYSTEM','','',"You're not registered",1)
		if "may not reregister" in line2:
			display_message('SYSTEM','','',"You can't reregister",1)
		if "enough parameters" in line2:
			display_message('SYSTEM','','',"Error: not enough parameters supplied to command",1)
		if "isn't among the privileged" in line2:
			display_message('SYSTEM','','',"Registration refused (server isn't setup to allow connections from your host)",1)
		if "Password incorrect" in line2:
			display_message('SYSTEM','','',"Permission denied (incorrect password)",1)
		if "banned from this server" in line2:
			display_message('SYSTEM','','',"You are banned from this server",1)
		if "kill a server" in line2:
			display_message('SYSTEM','','',"Permission denied (you can't kill a server)",1)
		if "O-lines for your host" in line2:
			display_message('SYSTEM','','',"Error: no O-lines for your host",1)
		if "Unknown MODE flag" in line2:
			display_message('SYSTEM','','',"Error: unknown MODE flag",1)
		if "change mode for other users" in line2:
			display_message('SYSTEM','','',"Permission denied (can't change mode for other users)",1)
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
		if c.Channel == channel:
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
				display_message('SYSTEM','','',"Can't change nickname (not connected to a server)",1)
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
				display_message('SYSTEM','','',"Can't send CTCP action message (not connected to a server)",1)
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
				display_message('OUTPRIVATE',target,NICKNAME,msg,1)
			else:
				display_message('SYSTEM','','',"Can't send message (not connected to a server)",1)
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
				display_message('OUTNOTICE',target,NICKNAME,msg,1)
			else:
				display_message('SYSTEM','','',"Can't send notice (not connected to a server)",1)
			return True

	if len(tokens) >= 1 and tokens[0].lower() == '/notice':
		display_message('SYSTEM','','',"USAGE: /notice TARGET MESSAGE",1)
		return True

def handleInput(text):
	global GUI
	global CLIENT
	global CHANNEL

	if len(text)>=1 and text[0] == '/':
		if not handleCommands(text):
			display_message('SYSTEM','','',f"Unrecognized command: {text}",1)
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
	global MESSAGE_TEMPLATE
	global CHAT_TEMPLATE
	global CHANNEL
	if mtype.lower() == 'public':
		padded_user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE + 1)
		response = CHAT_TEMPLATE.replace('!COLOR!',PUBLIC_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'private':
		padded_user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
		response = PRIVATE_TEMPLATE.replace('!COLOR!',PRIVATE_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'outprivate':
		padded_user = pad_nick(f"{user}->{channel}",MAXIMUM_NICK_DISPLAY_SIZE)
		response = PRIVATE_TEMPLATE.replace('!COLOR!',PRIVATE_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'outnotice':
		padded_user = pad_nick(f"{user}->{channel}",MAXIMUM_NICK_DISPLAY_SIZE)
		response = PRIVATE_TEMPLATE.replace('!COLOR!',NOTICE_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'notice':
		padded_user = pad_nick(user,MAXIMUM_NICK_DISPLAY_SIZE)
		response = PRIVATE_TEMPLATE.replace('!COLOR!',NOTICE_MESSAGE_COLOR)
		response = response.replace('!USER!',f"<b>{padded_user}</b>")
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'action':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',ACTION_MESSAGE_COLOR)
		response = response.replace('!TEXT!',f"{user} {message}")
	elif mtype.lower() == 'system':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'join':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'part':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'topic':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'kick':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'mode':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'usermode':
		response = MESSAGE_TEMPLATE.replace('!COLOR!',SYSTEM_MESSAGE_COLOR)
		response = response.replace('!TEXT!',message)
	elif mtype.lower() == 'ascii':
		response = f"<pre>{message}</pre>"
	elif mtype.lower() == 'raw':
		response = f"{message}"
	else:
		return
	doPrint = True
	if mtype.lower() == 'topic' and channel != CHANNEL: doPrint = False
	if doPrint:
		GUI.writeText(response)
	if store == 1:
		# store message
		if channel == '' or channel == NICKNAME or channel == '*':
			m = Chat(mtype,SERVER,user,message)
			storeChat(m)
			if CHANNEL != '':
				m = Chat(mtype,CHANNEL,user,message)
				storeChat(m)
		else:
			if channel != '' and len(channel)>=1:
				if channel[0] != '#' or channel[0] !='&': return
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

# ================
# | MAIN PROGRAM |
# ================

if __name__ == '__main__':

	# Spawn the GUI
	global GUI
	GUI = qpIRC_GUI()

	display_message('ASCII','','',LOGO,1)
	display_message('RAW','','',f"<b>{APPLICATION} {VERSION}</b><br><i>{DESCRIPTION}</i>",1)

	if os.path.isfile(COLOR_INFORMATION_FILE):
		with open(COLOR_INFORMATION_FILE, "r") as read_color:
			data = json.load(read_color)
			SYSTEM_MESSAGE_COLOR = data["system"]
			PUBLIC_MESSAGE_COLOR = data["public"]
			PRIVATE_MESSAGE_COLOR = data["private"]
			NOTICE_MESSAGE_COLOR = data["notice"]
			ACTION_MESSAGE_COLOR = data["action"]
			BACKGROUND_COLOR = data["background"]
			GUI.chatDisplay.setStyleSheet(f"background-color: \"{BACKGROUND_COLOR}\";")


	# Load user information if present
	if os.path.isfile(USER_INFORMATION_FILE):
		with open(USER_INFORMATION_FILE, "r") as read_user:
			data = json.load(read_user)
			if len(data) != 3:
				display_message('SYSTEM','','',f"User data in {USER_INFORMATION_FILE} is malformed",1)
			else:
				NICKNAME = data[0]
				REALNAME = data[1]
				USERNAME = data[2]
				display_message('SYSTEM','','',f"Saved user settings loaded",1)

	# Load server information if present
	if os.path.isfile(SERVER_INFORMATION_FILE):
		with open(SERVER_INFORMATION_FILE, "r") as read_serv:
			data = json.load(read_serv)
			if len(data) != 4:
				display_message('SYSTEM','','',f"Server data in {SERVER_INFORMATION_FILE} is malformed",1)
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
