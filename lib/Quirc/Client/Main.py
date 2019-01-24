
import sys

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

import Quirc.Client.Server as Server
import Quirc.Client.Channel as Channel
import Quirc.Client.User as User
import Quirc.Dialog.Connect as Connect
import Quirc.Dialog.Connecting as Connecting
import Quirc.Dialog.UserInfo as UserInfo
import Quirc.Dialog.Colors as Colors

from Quirc.Settings import *
from Quirc.Format import *

class Window(QMainWindow):

	def closeAllWindows(self):
		for c in self.CHANNELS:
			c.closeWindow()
		self.subWindow.close()
		self.CHANNELS = []
		self.HOST = ''
		self.PORT = 0
		self.ACTIVE = ''

	def partChannel(self,channel):
		nc = []
		for c in self.CHANNELS:
			if c.Channel == channel:
				c.closeWindow()
				continue
			nc.append(c)
		self.CHANNELS = nc

	def addUsersToChannel(self,channel,users):
		for c in self.CHANNELS:
			if c.Channel == channel:
				c.gotNames(users)

	def endOfUserList(self,channel):
		for c in self.CHANNELS:
			if c.Channel == channel:
				c.buildNames()

	def writeToUser(self,user,text):
		for c in self.CHANNELS:
			if c.Nick == user:
				c.writeText(text)
				return
		cw = QMdiSubWindow()
		chan = User.Window(user,self.CLIENT,self,cw)
		cw.setWidget(chan)
		cw.setWindowTitle(user)
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create('Windows'))
		self.CHANNELS.append(chan)
		chan.writeText(text)
		cw.show()
		cw.resize(self.iWidth,self.iHeight)

	def isInChannel(self,channel):
		for c in self.CHANNELS:
			if c.Channel == channel:
				return True
		return False

	def writeToChannel(self,channel,text):
		for c in self.CHANNELS:
			if c.Channel == channel:
				c.writeText(text)
				return
		cw = QMdiSubWindow()
		chan = Channel.Window(channel,self.CLIENT,self,cw)
		cw.setWidget(chan)
		cw.setWindowTitle(channel)
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create('Windows'))
		self.CHANNELS.append(chan)
		chan.writeText(text)
		cw.show()
		cw.resize(self.iWidth,self.iHeight)

	def channelTopic(self,channel,text):
		for c in self.CHANNELS:
			if c.Channel == channel:
				c.setTopic(text)
				return

	def refreshAllUserLists(self):
		for c in self.CHANNELS:
			self.CLIENT.sendLine(f"NAMES {c.Channel}")

	def writeToActiveWindow(self,text):
		if self.ACTIVE != '':
			if len(self.ACTIVE)>1:
				if self.ACTIVE[0] == '#':
					self.writeToChannel(self.ACTIVE,text)
					return
				if self.ACTIVE[0] == '&':
					self.writeToChannel(self.ACTIVE,text)
					return

	def writeToServer(self,text):
		self.serverWindow.writeText(text)

	def cascadeWindows(self):
		self.MDI.cascadeSubWindows()

	def tileWindows(self):
		self.MDI.tileSubWindows()

	def connectDialog(self):
		x = Connect.Dialog(parent=self)
		x.show()

	def userDialog(self):
		x = UserInfo.Dialog(parent=self)
		x.show()

	def updateAllColors(self,obj):
		for c in self.CHANNELS:
			c.setColors(uColors)

	def userColor(self):
		x = Colors.Dialog(parent=self)
		x.show()
			#self.serverWindow.setColors(uColors)

	def menuDisconnect(self):
		for c in self.CHANNELS:
			c.closeWindow()
		self.subWindow.close()
		self.CHANNELS = []
		self.HOST = ''
		self.PORT = 0
		self.ACTIVE = ''
		self.CLIENT.quit()

	def connecting(self,host):
		self.CONNECTING = Connecting.Dialog(host,parent=self)

	def setNetworkInformation(self,host,port):
		self.HOST = host
		self.PORT = port

	def connected(self,obj):
		self.CONNECTING.connected()
		self.CONNECTING = None
		self.CLIENT = obj

		cw = QMdiSubWindow()
		self.serverWindow = Server.Window(obj,self,cw,parent=self)
		self.subWindow = cw
		cw.setWidget(self.serverWindow)
		cw.setWindowTitle(f"{self.HOST}:{self.PORT}")
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create('Windows'))

		cw.setWindowFlags(
			Qt.WindowMinMaxButtonsHint |
			Qt.WindowTitleHint
			)

		self.serverWindow.show()
		cw.resize(self.iWidth,self.iHeight)

	def exitDialog(self):
		global app
		app.quit()

	def activeWindow(self,subwindow):
		try:
			self.ACTIVE = subwindow.windowTitle()
		except:
			self.ACTIVE = ''

	def restartDialog(self):
		self.RESTART()

	def loadSettings(self):
		if os.path.isfile(WINDOW_INFORMATION_FILE):
			with open(WINDOW_INFORMATION_FILE, "r") as read_win:
				data = json.load(read_win)
				self.iWidth = data["initialWidth"]
				self.iHeight = data["initialHeight"]
		else:
			self.iWidth = 640
			self.iHeight = 480

	def __init__(self,tcp_func,ssl_func,ssl_available,restart_func,parent=None):
		super(Window, self).__init__(parent)
		self.CHANNELS = []
		self.SERVER = None
		self.CLIENT = None
		self.HOST = ''
		self.PORT = 0
		self.ACTIVE = ''
		self.TCP_Connect = tcp_func
		self.SSL_Connect = ssl_func
		self.SSL_AVAILABLE = False
		self.subWindow = None
		self.CONNECTING = None
		self.RESTART = restart_func
		self.loadSettings()

		self.MDI = QMdiArea()

		self.setCentralWidget(self.MDI)

		pix = QPixmap(BACKGROUND)
		self.brush = QBrush(pix)
		self.MDI.setBackground(self.brush)

		self.setFont(QUIRC_TITLE_FONT)

		self.setWindowTitle(f"Quirc")
		self.setWindowIcon(QIcon(QUIRC_ICON))

		self.MDI.subWindowActivated.connect(self.activeWindow)

		menubar = self.menuBar()

		ircMenu = menubar.addMenu("IRC")

		self.actConnect = QAction(QIcon(CONNECT_ICON),"Connect to IRC",self)
		self.actConnect.triggered.connect(self.connectDialog)
		ircMenu.addAction(self.actConnect)

		self.actDisconnect = QAction(QIcon(DISCONNECT_ICON),"Disconnect from IRC",self)
		self.actDisconnect.triggered.connect(self.menuDisconnect)
		self.actDisconnect.setVisible(False)
		ircMenu.addAction(self.actDisconnect)
		self.actDisconnect.setEnabled(False)

		ircMenu.addSeparator()

		actRestart = QAction(QIcon(RESTART_ICON),"Restart Quirc",self)
		actRestart.triggered.connect(self.restartDialog)
		ircMenu.addAction(actRestart)

		actExit = QAction(QIcon(EXIT_ICON),"Exit",self)
		actExit.triggered.connect(self.exitDialog)
		ircMenu.addAction(actExit)

		setMenu = menubar.addMenu("Settings")

		actUser = QAction(QIcon(USER_ICON),"User Information",self)
		actUser.triggered.connect(self.userDialog)
		setMenu.addAction(actUser)

		actUserColor = QAction(QIcon(COLOR_ICON),"Colors",self)
		actUserColor.triggered.connect(self.userColor)
		setMenu.addAction(actUserColor)

		winMenu = menubar.addMenu("Windows")

		actCascade = QAction(QIcon(CASCADE_ICON),"Cascade",self)
		actCascade.triggered.connect(self.cascadeWindows)
		winMenu.addAction(actCascade)

		actTile = QAction(QIcon(TILE_ICON),"Tiled",self)
		actTile.triggered.connect(self.tileWindows)
		winMenu.addAction(actTile)

		window_width = self.width()
		window_height = self.height()
		image_width = 300
		image_height = 132
		
		self.show()

	def closeEvent(self, event):
		global app
		app.quit()

