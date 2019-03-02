
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
from quirc.commands import *

class Window(QWidget):

	def doResize(self):
		pass

	def hideMenu(self):
		pass

	def showMenu(self):
		pass

	def configureOptions(self):
		pass

	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			QDesktopServices.openUrl(url)
			self.chatDisplay.setSource(QUrl())
		else:
			#print(link)
			self.chatDisplay.setSource(QUrl())

	def closeEvent(self, event):
		self.chatDisplay.clear()
		self.ircInput.clear()
		self.parent.disconnectIRC()
		if self.parent.online:
			self.parent.disconnectIRC()
		self.close()

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

		if help_commands(txt,HELP_TYPE_SERVER,self,self.parent):
			# help got triggered
			return

		if shared_commands(txt,self.client,self,self.parent):
			# command got triggered
			return

		if self.parent.link_urls:
			txt = inject_www_links(text)

		#print(txt)

	def setIRCConnection(self,obj):
		self.client = obj

	def __init__(self,parent=None):
		super(Window,self).__init__(parent)

		self.client = None
		self.parent = parent

		self.online = True

		self.is_irc_channel = False

		self.chatDisplay = QTextBrowser(self)
		self.chatDisplay.setGeometry(QtCore.QRect(10, 10, 450, 425))
		self.chatDisplay.setObjectName("chatDisplay")

		self.ircInput = QLineEdit(self)
		self.ircInput.setGeometry(QtCore.QRect(10, self.chatDisplay.height()+15, 605, 30))
		self.ircInput.setObjectName("ircInput")
		self.ircInput.returnPressed.connect(self.manageUserInput)

		self.chatDisplay.setStyleSheet(f"background-color: \"{self.parent.background_color}\"; color:  \"{self.parent.chat_color}\";")
		self.ircInput.setStyleSheet(f"background-color: \"{self.parent.background_color}\"; color:  \"{self.parent.chat_color}\";")

		self.chatDisplay.setOpenLinks(False)
		self.chatDisplay.anchorClicked.connect(self.linkClicked)

		# self.chatDisplay.setFont(QUIRC_FONT)
		# self.ircInput.setFont(QUIRC_FONT)

		self.setGeometry(QtCore.QRect(10, 10, 640, 480))

	def resizeEvent(self,resizeEvent):

		window_width = self.width()
		window_height = self.height()

		base_x = 0
		base_y = 3

		cdisplay_height = window_height - 30
		cdisplay_width = window_width

		input_width = cdisplay_width
		input_height = 25

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width(), input_height))