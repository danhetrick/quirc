
import sys

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from Quirc.Settings import *
from Quirc.Format import *
from Quirc.Commands import *

class Window(QWidget):

	def reloadColors(self):
		self.Colors = loadColorSettings(COLOR_FILE)

	def setColors(self,obj):
		self.Colors = obj

	def closeEvent(self, event):
		pass

	def closeWindow(self):
		self.close()
		self.SUBWINDOW.close()

	def __init__(self,nick,client,master,subwindow,parent=None):
		super(Window,self).__init__(parent)
		self.Nick = nick
		self.Channel = ''
		self.CLIENT = client
		self.GUI = master
		self.SUBWINDOW = subwindow
		self.loadSettings()

		self.Colors = loadColorSettings(COLOR_FILE)

		self.createUI()

	def writeText(self,text):
		self.chatDisplay.append(text)
		self.chatDisplay.moveCursor(QTextCursor.End)

	def writeHtml(self,text):
		self.chatDisplay.insertHtml(f"{text}")
		self.chatDisplay.moveCursor(QTextCursor.End)

	def displayLastLine(self):
		self.chatDisplay.moveCursor(QTextCursor.End)

	def createUI(self):
		self.setWindowTitle(f"{self.Nick}")

		self.setWindowIcon(QIcon(USER_ICON))

		self.chatDisplay = QTextBrowser(self)
		self.chatDisplay.setGeometry(QtCore.QRect(10, 10, 450, 425))
		self.chatDisplay.setObjectName("chatDisplay")

		sp = [ICON_DIRECTORY,RESOURCE_DIRECTORY]
		self.chatDisplay.setSearchPaths(sp)

		self.ircInput = QLineEdit(self)
		self.ircInput.setGeometry(QtCore.QRect(10, self.chatDisplay.height()+15, 605, 30))
		self.ircInput.setObjectName("ircInput")
		self.ircInput.returnPressed.connect(self.manageUserInput)

		self.chatDisplay.setFont(QUIRC_FONT)
		self.ircInput.setFont(QUIRC_FONT)

		self.chatDisplay.setStyleSheet(f"background-color: \"{self.Colors.Background}\"; color:  \"{self.Colors.Normal}\";")
		self.ircInput.setStyleSheet(f"background-color: \"{self.Colors.Background}\"; color:  \"{self.Colors.Normal}\";")

		self.setGeometry(QtCore.QRect(10, 10, 640, 480))


	def resizeEvent(self,resizeEvent):

		window_width = self.width()
		window_height = self.height()

		base_x = 3
		base_y = 5

		cdisplay_height = window_height - 35
		cdisplay_width = window_width - 10

		input_width = cdisplay_width
		input_height = 25

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width(), input_height))


	def manageUserInput(self):
		txt = self.ircInput.text()
		self.ircInput.setText('')

		if not userHandler(txt,self.CLIENT,self,self.GUI):
			self.CLIENT.msg(self.Nick,txt,length=MAXIMUM_IRC_MESSAGE_LENGTH)
			# Inject links
			if self.linkURL: txt = format_links(txt)
			d = nolink_chat_message(self.Colors.Self,self.CLIENT.nickname,txt)
			self.chatDisplay.append(d)
			self.chatDisplay.moveCursor(QTextCursor.End)
			
	def loadSettings(self):
		if os.path.isfile(WINDOW_INFORMATION_FILE):
			with open(WINDOW_INFORMATION_FILE, "r") as read_win:
				data = json.load(read_win)
				self.linkURL = data["linkURL"]
		else:
			self.linkURL = True

