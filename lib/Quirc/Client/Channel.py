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

	def __init__(self,channel,client,master,subwindow,parent=None):
		super(Window,self).__init__(parent)
		self.Channel = channel
		self.CLIENT = client
		self.GUI = master
		self.SUBWINDOW = subwindow
		self.Nick = ''
		self.Users = []
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

	def gotNames(self,names):
		for n in names:
			if n in self.Users: continue
			self.Users.append(n)

	def buildNames(self):
		self.userList.clear()
		self.Users = self.sortNicks(self.Users)
		for n in self.Users:
			self.addUser(n)
		self.Users = []

	def sortNicks(self,users):
		ops = []
		voiced = []
		normal = []
		sortnicks = []
		for nick in users:
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

	def closeEvent(self, event):
		self.CLIENT.part(self.Channel)
		self.close()

	def closeWindow(self):
		self.CLIENT.part(self.Channel)
		self.close()
		self.SUBWINDOW.close()

	def setTopic(self,topic):
		if topic == '':
			self.setWindowTitle(f"{self.Channel}")
		else:
			self.setWindowTitle(f"{self.Channel} - {topic}")

	def createUI(self):
		
		self.setWindowTitle(f"{self.Channel}")

		self.setWindowIcon(QIcon(CHAT_ICON))

		self.chatDisplay = QTextBrowser(self)
		self.chatDisplay.setGeometry(QtCore.QRect(10, 10, 450, 425))
		self.chatDisplay.setObjectName("chatDisplay")

		self.chatDisplay.setOpenLinks(False)
		self.chatDisplay.anchorClicked.connect(self.linkClicked)

		sp = [ICON_DIRECTORY,RESOURCE_DIRECTORY]
		self.chatDisplay.setSearchPaths(sp)

		self.userList = QListWidget(self)
		self.userList.setGeometry(QtCore.QRect(self.chatDisplay.width()+15, 10, 150, 425))
		self.userList.setObjectName("userList")

		self.ircInput = QLineEdit(self)
		self.ircInput.setGeometry(QtCore.QRect(10, self.chatDisplay.height()+15, 605, 30))
		self.ircInput.setObjectName("ircInput")
		self.ircInput.returnPressed.connect(self.manageUserInput)

		self.chatDisplay.setFont(QUIRC_FONT)
		self.ircInput.setFont(QUIRC_FONT)
		self.userList.setFont(QUIRC_FONT_BOLD)

		self.chatDisplay.setStyleSheet(f"background-color: \"{self.Colors.Background}\"; color:  \"{self.Colors.Normal}\";")
		self.ircInput.setStyleSheet(f"background-color: \"{self.Colors.Background}\"; color:  \"{self.Colors.Normal}\";")
		self.userList.setStyleSheet(f"background-color: \"{self.Colors.Background}\"; color:  \"{self.Colors.Normal}\";")

		self.setGeometry(QtCore.QRect(10, 10, 640, 480))

	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			txt = self.chatDisplay.toHtml()
			QDesktopServices.openUrl(url)
			self.chatDisplay.setText(txt)
			self.chatDisplay.moveCursor(QTextCursor.End)
		else:
			d = quirc_msg(f"Private chat with {link}")
			self.GUI.writeToUser(link,d)

	def manageUserInput(self):
		txt = self.ircInput.text()
		self.ircInput.setText('')

		if not channelHandler(txt,self.CLIENT,self,self.GUI):
			self.CLIENT.msg(self.Channel,txt,length=MAXIMUM_IRC_MESSAGE_LENGTH)
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


	def resizeEvent(self,resizeEvent):

		window_width = self.width()
		window_height = self.height()

		base_x = 3
		base_y = 5

		cdisplay_height = window_height - 35
		cdisplay_width = window_width - 160

		ulist_width = 150
		ulist_height = cdisplay_height

		input_width = cdisplay_width + 3 + ulist_width
		input_height = 25

		self.chatDisplay.setGeometry(QtCore.QRect(base_x, base_y, cdisplay_width, cdisplay_height))
		self.userList.setGeometry(QtCore.QRect(base_x + cdisplay_width + 3, base_y, ulist_width, ulist_height))
		self.ircInput.setGeometry(QtCore.QRect(base_x, cdisplay_height + base_y + 3 , self.chatDisplay.width() + self.userList.width() + 3, input_height))
