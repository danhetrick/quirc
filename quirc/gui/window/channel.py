
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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from quirc.common import *

import quirc.gui.dialog.info as InfoDialog
import quirc.gui.dialog.channel_key as ChannelKeyDialog
import quirc.gui.dialog.channel_limit as ChannelLimitDialog

from quirc.commands import *

class Window(QMainWindow):

	def closeEvent(self, event):
		if self.online:
			self.client.part(self.channel)
			self.parent.removeChannel(self.channel)
		self.chatDisplay.clear()
		self.userList.clear()
		self.ircInput.clear()
		self.close()

	def setUsers(self,ulist):
		self.is_op = False
		self.voiced = False
		self.userList.clear()
		for n in ulist:
			if '@' in n:
				if self.nickname in n:
					self.is_op = True
			if '+' in n:
				if self.nickname in n:
					self.voiced = True
			self.userList.addItem(n)
		self.configureOptions()

	def writeText(self,text):
		if self.parent.link_urls:
			text = inject_www_links(text,self.parent.link_color)
		self.chatDisplay.append(text)
		self.chatDisplay.moveCursor(QTextCursor.End)

	def writeHtml(self,text):
		self.chatDisplay.insertHtml(f"{text}")
		self.chatDisplay.moveCursor(QTextCursor.End)

	def displayLastLine(self):
		self.chatDisplay.moveCursor(QTextCursor.End)

	def manageUserInput(self):
		txt = self.ircInput.text()
		self.ircInput.setText('')

		if help_commands(txt,HELP_TYPE_CHANNEL,self,self.parent):
			# help got triggered
			return

		if shared_commands(txt,self.client,self,self.parent):
			# command got triggered
			return

		if channel_commands(txt,self.channel,self.client,self,self.parent):
			# command got triggered
			return

		self.client.privmsg(self.channel,txt)

		d = chat_message(self.parent.myusername_color,self.parent.background_color,self.parent.chat_color,self.nickname,txt,self.parent.maxnicklength)
		self.writeText(d)

		#print(self.info)

	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			QDesktopServices.openUrl(url)
			self.chatDisplay.setSource(QUrl())
		else:
			self.chatDisplay.setSource(QUrl())
			self.parent.raiseOrCreateUserWindow(link)

	def copyToClipboard(self,data):
		cb = QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(f"{data}", mode=cb.Clipboard)

	def copyTopic(self):
		self.copyToClipboard(self.topic)

	def chanInfo(self):
		x = InfoDialog.Dialog(self.info,parent=self)
		x.show()

	def __init__(self,channel,nickname,client,subwindow,parent=None):
		super(Window,self).__init__(parent)

		self.channel = channel
		self.client = client
		self.parent = parent
		self.nickname = nickname
		self.subwindow = subwindow

		self.is_irc_channel = True

		self.is_op = False
		self.voiced = False

		self.online = True

		self.topic = ''

		self.info = [channel,'',0,0,0,0,0,0,0,0]

		self.setWindowTitle(f"  {self.channel}")

		self.chatDisplay = QTextBrowser(self)
		self.chatDisplay.setGeometry(QtCore.QRect(10, 10, 450, 425))
		self.chatDisplay.setObjectName("chatDisplay")

		self.chatDisplay.anchorClicked.connect(self.linkClicked)

		self.userList = QListWidget(self)
		self.userList.setGeometry(QtCore.QRect(self.chatDisplay.width()+15, 10, 150, 425))
		self.userList.setObjectName("userList")

		self.ircInput = QLineEdit(self)
		self.ircInput.setGeometry(QtCore.QRect(10, self.chatDisplay.height()+15, 605, 30))
		self.ircInput.setObjectName("ircInput")
		self.ircInput.returnPressed.connect(self.manageUserInput)

		self.chatDisplay.setStyleSheet(f"background-color: \"{self.parent.background_color}\"; color:  \"{self.parent.chat_color}\";")
		self.userList.setStyleSheet(f"background-color: \"{self.parent.background_color}\"; color:  \"{self.parent.chat_color}\";")
		self.ircInput.setStyleSheet(f"background-color: \"{self.parent.background_color}\"; color:  \"{self.parent.chat_color}\";")

		# self.STATUS = self.statusBar()

		# self.status_icon = QLabel()
		# self.status_icon.setPixmap(QIcon(RESOURCE_ICON_USER).pixmap(16,16))
		# self.status_text = QLabel("  Normal user")
		# self.status_text.setFont(self.parent.default_font)
		# self.STATUS.addWidget(self.status_icon)
		# self.STATUS.addWidget(self.status_text)

		self.channel_menubar = self.menuBar()

		# Quirc Menu
		channelMenu = self.channel_menubar.addMenu("Channel")

		self.actChanInfo = QAction(QIcon(RESOURCE_ICON_HASH),"Details",self)
		self.actChanInfo.triggered.connect(self.chanInfo)
		channelMenu.addAction(self.actChanInfo)

		self.actCopyTopic = QAction(QIcon(RESOURCE_ICON_CLIPBOARD),"Copy topic to clipboard",self)
		self.actCopyTopic.triggered.connect(self.copyTopic)
		channelMenu.addAction(self.actCopyTopic)

		self.actChannel1 = QAction(QIcon(RESOURCE_ICON_LEAVE),"Leave Channel",self)
		self.actChannel1.triggered.connect(self.close)
		channelMenu.addAction(self.actChannel1)

		# Options Menu
		optionsMenu = self.channel_menubar.addMenu("Options")

		self.userType = QAction(QIcon(RESOURCE_IMAGE_USER),"Normal User",self)
		optionsMenu.addAction(self.userType)

		optionsMenu.addSeparator()

		self.actKey = QAction("Channel key",self)
		self.actKey.triggered.connect(self.setKey)
		optionsMenu.addAction(self.actKey)

		self.actLimit = QAction("User limit",self)
		self.actLimit.triggered.connect(self.setLimit)
		optionsMenu.addAction(self.actLimit)

		self.optModerated = QAction("Moderated",self,checkable=True)
		self.optModerated.setChecked(False)
		self.optModerated.triggered.connect(self.toggleModerated)
		optionsMenu.addAction(self.optModerated)

		self.optInvite = QAction("Invitation Only",self,checkable=True)
		self.optInvite.setChecked(False)
		self.optInvite.triggered.connect(self.toggleInvite)
		optionsMenu.addAction(self.optInvite)

		self.optExtern = QAction("No External Messages",self,checkable=True)
		self.optExtern.setChecked(False)
		self.optExtern.triggered.connect(self.toggleExtern)
		optionsMenu.addAction(self.optExtern)

		self.optTopic = QAction("Topic locked",self,checkable=True)
		self.optTopic.setChecked(False)
		self.optTopic.triggered.connect(self.toggleTopic)
		optionsMenu.addAction(self.optTopic)

		self.optProtected = QAction("Private",self,checkable=True)
		self.optProtected.setChecked(False)
		self.optProtected.triggered.connect(self.toggleProtect)
		optionsMenu.addAction(self.optProtected)

		self.optSecret = QAction("Secret",self,checkable=True)
		self.optSecret.setChecked(False)
		self.optSecret.triggered.connect(self.toggleSecret)
		optionsMenu.addAction(self.optSecret)

		self.optColors = QAction("No colors",self,checkable=True)
		self.optColors.setChecked(False)
		self.optColors.triggered.connect(self.toggleColors)
		optionsMenu.addAction(self.optColors)

		#self.channel_menubar.hide()
		self.menu_hidden = False

	def hideMenu(self):
		self.channel_menubar.hide()
		self.menu_hidden = True

	def showMenu(self):
		self.channel_menubar.show()
		self.menu_hidden = False

	def setLimit(self):
		x = ChannelLimitDialog.Dialog(parent=self)
		mylimit = x.get_limit_information(self.client,parent=self)

		if not mylimit:
			# User hit cancel button in dialog
			return

		# client set

	def setKey(self):
		# set channel key
		# ChannelKeyDialog
		x = ChannelKeyDialog.Dialog()
		if len(self.info[CHANNEL_INFO_KEY])>0:
			mykey = x.get_key_information("Remove channel key",parent=self)
		else:
			mykey = x.get_key_information("Set channel key",parent=self)

		if not mykey:
			# User hit cancel button in dialog
			return

		if len(self.info[CHANNEL_INFO_KEY])>0:
			self.client.send_items('MODE', self.channel, "-k", mykey)
		else:
			self.client.send_items('MODE', self.channel, "+k", mykey)


	def toggleColors(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+c")
		else:
			self.client.send_items('MODE', self.channel, "-c")

	def toggleModerated(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+m")
		else:
			self.client.send_items('MODE', self.channel, "-m")

	def toggleSecret(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+s")
		else:
			self.client.send_items('MODE', self.channel, "-s")

	def toggleProtect(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+p")
		else:
			self.client.send_items('MODE', self.channel, "-p")

	def toggleTopic(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+t")
		else:
			self.client.send_items('MODE', self.channel, "-t")

	def toggleExtern(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+n")
		else:
			self.client.send_items('MODE', self.channel, "-n")

	def toggleInvite(self,state):
		if state:
			self.client.send_items('MODE', self.channel, "+i")
		else:
			self.client.send_items('MODE', self.channel, "-i")

	def configureOptions(self):

		if self.info[CHANNEL_INFO_INVITEONLY] == 1:
			self.optInvite.setChecked(True)
		else:
			self.optInvite.setChecked(False)

		if self.info[CHANNEL_INFO_ALLOWEXTERNAL] == 1:
			self.optExtern.setChecked(True)
		else:
			self.optExtern.setChecked(False)

		if self.info[CHANNEL_INFO_TOPICLOCKED] == 1:
			self.optTopic.setChecked(True)
		else:
			self.optTopic.setChecked(False)

		if self.info[CHANNEL_INFO_PROTECTED] == 1:
			self.optProtected.setChecked(True)
		else:
			self.optProtected.setChecked(False)

		if self.info[CHANNEL_INFO_SECRET] == 1:
			self.optSecret.setChecked(True)
		else:
			self.optSecret.setChecked(False)

		if self.info[CHANNEL_INFO_MODERATED] == 1:
			self.optModerated.setChecked(True)
		else:
			self.optModerated.setChecked(False)

		if self.info[CHANNEL_INFO_NOCOLORS] == 1:
			self.optColors.setChecked(True)
		else:
			self.optColors.setChecked(False)

		if self.is_op:
			self.actLimit.setEnabled(True)
			self.actKey.setEnabled(True)
			self.optModerated.setEnabled(True)
			self.optInvite.setEnabled(True)
			self.optExtern.setEnabled(True)
			self.optTopic.setEnabled(True)
			self.optProtected.setEnabled(True)
			self.optSecret.setEnabled(True)
			self.optColors.setEnabled(True)
		else:
			self.actLimit.setEnabled(False)
			self.actKey.setEnabled(False)
			self.optModerated.setEnabled(False)
			self.optInvite.setEnabled(False)
			self.optExtern.setEnabled(False)
			self.optTopic.setEnabled(False)
			self.optProtected.setEnabled(False)
			self.optSecret.setEnabled(False)
			self.optColors.setEnabled(False)

		if self.is_op:
			self.userType.setText("Channel operator")
			#self.status_text.setText(f"  Channel operator")
		elif self.voiced:
			self.userType.setText("Voiced user")
			#self.status_text.setText(f"  Voiced user")
		else:
			self.userType.setText("Normal user")
			#self.status_text.setText(f"  Normal user")


	def doResize(self):

		window_width = self.width()
		window_height = self.height()

		base_x = 0
		# base_y = 22

		# cdisplay_height = window_height - 50
		cdisplay_width = window_width - 155

		if self.menu_hidden:
			cdisplay_height = window_height - 30
			base_y = 2
		else:
			cdisplay_height = window_height - 50
			base_y = 22


		ulist_width = 150
		ulist_height = cdisplay_height

		input_width = cdisplay_width + 3 + ulist_width
		input_height = 25

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.userList.setGeometry(QtCore.QRect(base_x + cdisplay_width + 3, base_y, ulist_width, ulist_height))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width() + self.userList.width() + 3, input_height))

	def resizeEvent(self,resizeEvent):

		window_width = self.width()
		window_height = self.height()

		base_x = 0
		# base_y = 22

		# cdisplay_height = window_height - 50
		cdisplay_width = window_width - 155

		if self.menu_hidden:
			cdisplay_height = window_height - 35
			base_y = 2
		else:
			cdisplay_height = window_height - 50
			base_y = 22


		ulist_width = 150
		ulist_height = cdisplay_height

		input_width = cdisplay_width + 3 + ulist_width
		input_height = 25

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.userList.setGeometry(QtCore.QRect(base_x + cdisplay_width + 3, base_y, ulist_width, ulist_height))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width() + self.userList.width() + 3, input_height))


