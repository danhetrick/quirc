
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

import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from quirc.irc.client import QuircClientThread

import quirc.gui.dialog.connect as ConnectDialog
import quirc.gui.dialog.join_channel as JoinDialog
import quirc.gui.dialog.new_nick as NickDialog
import quirc.gui.dialog.user_info as UserDialog
import quirc.gui.dialog.editor as EditorDialog
import quirc.gui.dialog.connect_stored as ConnectStoredDialog
import quirc.gui.dialog.html as HTMLDialog

from quirc.common import *

from quirc.gui.window.server import Window as ServerWindow
from quirc.gui.window.channel import Window as ChannelWindow
from quirc.gui.window.user import Window as UserWindow
from quirc.gui.dialog.about import Window as AboutDialog

from quirc.script import QuircScriptThread
from quirc.script import Script


from irc.client import NickMask

from collections import defaultdict

class Quirc(QMainWindow):

	def tick(self):
		self.uptime = self.uptime + 1

	def clientIsUsingSSL(self):
		self.status_icon.setPixmap(self.SSL_ICON)
		self.status_text.setText(f"  Connected via SSL/TLS to {self.host}:{str(self.port)}")

	def clientIsNotUsingSSL(self):
		self.status_icon.setPixmap(self.CONNECT_ICON)
		self.status_text.setText(f"  Connected to {self.host}:{str(self.port)}")

	def clientIsDisconnected(self):
		self.status_icon.setPixmap(self.DISCONNECTED_ICON)
		self.status_text.setText("  Disconnected")

	def __init__(self,app,restart_func,parent=None):
		super(Quirc, self).__init__(parent)

		# myStyle = QuircStyle('Fusion')
		# self.setStyle(myStyle)

		self.app = app
		self.RESTART = restart_func
		self.users = defaultdict(list)
		self.chatlog = defaultdict(list)

		self.skipNextError = False

		self.CONNECT_ICON = QIcon(RESOURCE_ICON_CONNECT).pixmap(16,16)
		self.SSL_ICON = QIcon(RESOURCE_ICON_SSL).pixmap(16,16)
		self.DISCONNECTED_ICON = QIcon(RESOURCE_ICON_DISCONNECT).pixmap(16,16)

		self.editorWindow = None
		self.editorSubWindow = None

		#self.autoHideMenu = False
		self.useFloatingMenu = False

		self.useChannelMenu = True

		self.nickname = ''

		self.online = False
		self.useSSL = False

		self.host = ''
		self.port = 0

		self.windows = []

		self.uptime = 0

		self.topic = ''

		self.link_urls = LINK_URLS_IN_CHAT
		self.link_users = LINK_USERNAMES_IN_CHAT

		self.maxnicklength = MAXIMUM_NICK_DISPLAY_SIZE

		self.username_color = "blue"
		self.myusername_color = "red"
		self.background_color = "white"
		self.action_color = "green"
		self.chat_color = "black"
		self.notice_color = "purple"
		self.system_color = "darkorange"
		self.motd_color = "blue"
		self.error_color = "red"
		self.font_size = DEFAULT_FONT_SIZE
		self.user_size = USERLIST_FONT_SIZE
		self.big_size = BIG_FONT_SIZE
		self.huge_size = HUGE_FONT_SIZE
		self.link_color = "purple"

		# Set this to a string of HTML formatting tags to apply to system text
		# For example: bold+italic -> "bi"
		#              underline+bold+italic -> "ubi"
		# -or-
		# self.system_styles = ["small","strong","em"]
		self.system_styles = ""

		self.qtStyle = 'Windows'

		with open(RESOURCE_CHILD_STYLE_SHEET,"r") as fh:
			self.child_qss = fh.read()
		
		id = QFontDatabase.addApplicationFont(RESOURCE_FONT)
		_fontstr = QFontDatabase.applicationFontFamilies(id)[0]
		self.default_font = QFont(_fontstr, self.font_size)
		self.userlist_font = QFont(_fontstr, self.user_size)
		self.big_font = QFont(_fontstr, self.big_size)
		self.huge_font = QFont(_fontstr, self.huge_size)

		self.bold_userlist_font = QFont(_fontstr, self.user_size)
		self.bold_userlist_font.setBold(True)

		self.bold_default_font = QFont(_fontstr, self.font_size)
		self.bold_default_font.setBold(True)

		self.bold_big_font = QFont(_fontstr, self.big_size)
		self.bold_big_font.setBold(True)

		self.bold_huge_font = QFont(_fontstr, self.huge_size)
		self.bold_huge_font.setBold(True)

		app.setFont(self.default_font)

		self.MDI = QMdiArea()
		self.setCentralWidget(self.MDI)

		self.MDI.setFont(self.userlist_font)

		pix = QPixmap(RESOURCE_MDI_BACKGROUND)
		self.brush = QBrush(pix)
		self.MDI.setBackground(self.brush)

		self.setWindowTitle(f"{APPLICATION_NAME}")
		self.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))

		self.STATUS = self.statusBar()

		self.status_icon = QLabel()
		self.status_icon.setPixmap(self.DISCONNECTED_ICON)
		self.status_text = QLabel("  Disconnected")
		self.status_text.setFont(self.default_font)
		self.STATUS.addWidget(self.status_icon)
		self.STATUS.addWidget(self.status_text)

		self.menubar = self.menuBar()

		# Quirc Menu
		ircMenu = self.menubar.addMenu("IRC")

		# self.actRUN = QAction(QIcon(RESOURCE_ICON_CONNECT),"RUN TEST.TXT",self)
		# self.actRUN.triggered.connect(self.runScript)
		# ircMenu.addAction(self.actRUN)

		self.actConnect = QAction(QIcon(RESOURCE_ICON_CONNECT),"Connect to server",self)
		self.actConnect.triggered.connect(self.connectDialog)
		ircMenu.addAction(self.actConnect)

		self.actStored = QAction(QIcon(RESOURCE_ICON_BOOKMARK),"Network list",self)
		self.actStored.triggered.connect(self.storedDialog)
		ircMenu.addAction(self.actStored)

		self.actDisconnect = QAction(QIcon(RESOURCE_ICON_DISCONNECT),"Disconnect",self)
		self.actDisconnect.triggered.connect(self.disconnectIRC)
		ircMenu.addAction(self.actDisconnect)

		self.actConnect.setVisible(True)
		self.actStored.setVisible(True)
		self.actDisconnect.setVisible(False)

		ircMenu.addSeparator()

		self.actJoin = QAction(QIcon(RESOURCE_ICON_HASH),"Join channel",self)
		self.actJoin.triggered.connect(self.joinChannel)
		ircMenu.addAction(self.actJoin)

		self.actJoin.setEnabled(False)

		self.actNick = QAction(QIcon(RESOURCE_ICON_HASH),"New nickname",self)
		self.actNick.triggered.connect(self.newNick)
		ircMenu.addAction(self.actNick)

		self.actNick.setEnabled(False)

		ircMenu.addSeparator()

		self.actRestart = QAction(QIcon(RESOURCE_ICON_RESTART),"Restart",self)
		self.actRestart.triggered.connect(self.restartQuirc)
		ircMenu.addAction(self.actRestart)

		self.actExit = QAction(QIcon(RESOURCE_ICON_EXIT),"Exit",self)
		self.actExit.triggered.connect(self.exitQuirc)
		ircMenu.addAction(self.actExit)

		# Options Menu
		optMenu = self.menubar.addMenu("Options")

		self.optUEdit = QAction(QIcon(RESOURCE_IMAGE_PEN),"Edit user information",self)
		self.optUEdit.triggered.connect(self.editUserInfo)
		optMenu.addAction(self.optUEdit)

		optMenu.addSeparator()

		optFloatingMenu = QAction("Dockable menu",self,checkable=True)
		optFloatingMenu.setChecked(self.useFloatingMenu)
		optFloatingMenu.triggered.connect(self.toggleFloatingMenu)
		optMenu.addAction(optFloatingMenu)

		optChannelMenu = QAction("Channel menus",self,checkable=True)
		optChannelMenu.setChecked(self.useChannelMenu)
		optChannelMenu.triggered.connect(self.toggleChannelMenu)
		optMenu.addAction(optChannelMenu)

		# optAutohide = QAction("Autohide menu",self,checkable=True)
		# optAutohide.setChecked(self.autoHideMenu)
		# optAutohide.triggered.connect(self.toggleAutohide)
		# optMenu.addAction(optAutohide)

		optWeb = QAction("Clickable links",self,checkable=True)
		optWeb.setChecked(self.link_urls)
		optWeb.triggered.connect(self.toggleWWW)
		optMenu.addAction(optWeb)

		optUser = QAction("Clickable usernames",self,checkable=True)
		optUser.setChecked(self.link_users)
		optUser.triggered.connect(self.toggleUser)
		optMenu.addAction(optUser)

		optStatus = QAction("Status bar",self,checkable=True)
		optStatus.setChecked(True)
		optStatus.triggered.connect(self.toggleStatus)
		optMenu.addAction(optStatus)

		# Script Menu
		scriptMenu = self.menubar.addMenu("Script")

		self.actRun = QAction(QIcon(RESOURCE_IMAGE_RUN),"Execute Script",self)
		self.actRun.triggered.connect(self.runScript)
		scriptMenu.addAction(self.actRun)

		scriptMenu.addSeparator()

		self.actOpenScript = QAction(QIcon(RESOURCE_IMAGE_FILE),"Open Script",self)
		self.actOpenScript.triggered.connect(self.openEditor)
		scriptMenu.addAction(self.actOpenScript)

		self.actEditor = QAction(QIcon(RESOURCE_ICON_QUIRC),"Script Editor",self)
		self.actEditor.triggered.connect(self.runEditor)
		scriptMenu.addAction(self.actEditor)

		self.actRun.setEnabled(False)

		# Windows Menu
		winMenu = self.menubar.addMenu("Windows")

		actCascade = QAction(QIcon(RESOURCE_ICON_CASCADE),"Cascade",self)
		actCascade.triggered.connect(self.cascadeWindows)
		winMenu.addAction(actCascade)

		actTile = QAction(QIcon(RESOURCE_ICON_TILE),"Tiled",self)
		actTile.triggered.connect(self.tileWindows)
		winMenu.addAction(actTile)

		# Help Menu
		helpMenu = self.menubar.addMenu("Help")

		actwikiIRC = QAction(QIcon(RESOURCE_ICON_WWW),"IRC (Wikipedia)",self)
		actwikiIRC.triggered.connect(self.wiki)
		helpMenu.addAction(actwikiIRC)

		helpMenu.addSeparator()

		actRFC1459 = QAction(QIcon(RESOURCE_ICON_WWW),"RFC 1459",self)
		actRFC1459.triggered.connect(self.rfc1)
		helpMenu.addAction(actRFC1459)

		actRFC2812 = QAction(QIcon(RESOURCE_ICON_WWW),"RFC 2812",self)
		actRFC2812.triggered.connect(self.rfc2)
		helpMenu.addAction(actRFC2812)

		actRFC2813 = QAction(QIcon(RESOURCE_ICON_WWW),"RFC 2813",self)
		actRFC2813.triggered.connect(self.rfc3)
		helpMenu.addAction(actRFC2813)

		helpMenu.addSeparator()

		actGPL = QAction(QIcon(RESOURCE_ICON_COPYLEFT),"GPL 3.0",self)
		actGPL.triggered.connect(self.gplLink)
		helpMenu.addAction(actGPL)

		actAbout = QAction(QIcon(RESOURCE_ICON_ABOUT),"About Quirc",self)
		actAbout.triggered.connect(self.about)
		helpMenu.addAction(actAbout)

		self.menubar.setFont(self.userlist_font)
		ircMenu.setFont(self.userlist_font)
		winMenu.setFont(self.userlist_font)
		helpMenu.setFont(self.userlist_font)
		optMenu.setFont(self.userlist_font)

		# Floating Menu

		self.floatingMenu = QToolBar(self)
		self.addToolBar(Qt.TopToolBarArea,self.floatingMenu)
		self.floatingMenu.setIconSize(QSize(16,16))
		self.floatingMenu.setFloatable(True)

		ircButton = QPushButton("IRC")
		ircButton.setMenu(ircMenu)

		optButton = QPushButton("Options")
		optButton.setMenu(optMenu)

		scrButton = QPushButton("Script")
		scrButton.setMenu(scriptMenu)

		winButton = QPushButton("Windows")
		winButton.setMenu(winMenu)

		helpButton = QPushButton("Help")
		helpButton.setMenu(helpMenu)

		floatMenuButtonQss="""QPushButton {
			border: none;
			background: transparent;
			padding-left: 5px;
			padding-right: 5px;
			padding-top: 5px;
			padding-bottom: 5px;
		}
		QPushButton:focus:pressed{ background-color: gray; }
		QPushButton:hover{ background-color: gray; }
		QPushButton::menu-indicator { image: none; }
		QPushButton{ background: transparent; }"""

		ircButton.setStyleSheet(floatMenuButtonQss)
		optButton.setStyleSheet(floatMenuButtonQss)
		scrButton.setStyleSheet(floatMenuButtonQss)
		winButton.setStyleSheet(floatMenuButtonQss)
		helpButton.setStyleSheet(floatMenuButtonQss)

		ircButton.setFont(self.userlist_font)
		optButton.setFont(self.userlist_font)
		scrButton.setFont(self.userlist_font)
		winButton.setFont(self.userlist_font)
		helpButton.setFont(self.userlist_font)

		self.floatingMenu.addWidget(ircButton)
		self.floatingMenu.addWidget(optButton)
		self.floatingMenu.addWidget(scrButton)
		self.floatingMenu.addWidget(winButton)
		self.floatingMenu.addWidget(helpButton)

		if not self.useFloatingMenu:
			self.floatingMenu.hide()
			self.menubar.show()
		else:
			self.floatingMenu.show()
			self.menubar.hide()

		# self.setMouseTracking(True)
		# self.MDI.setMouseTracking(True)

		# if self.autoHideMenu:
		# 	self.menubar.hide()

	# def mouseMoveEvent(self,event):
	# 	if self.autoHideMenu:
	# 		pos = event.pos()
	# 		xval = pos.x()
	# 		yval = pos.y()


	# 		if yval <= 30:
	# 			if not self.menubar.isVisible():
	# 				self.menubar.show()
	# 			return

	# 		if self.menubar.isVisible():
	# 			self.menubar.hide()

	# def runScript(self):
	# 	self.qscript = QuircScriptThread(self.irc.connection,self,"test.txt")
	# 	self.qscript.start()

	def runScript(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"Open Quirc Script", INSTALL_DIRECTORY,"Quirc Script Files (*.quirc);;Text Files (*.txt);;All Files (*)", options=options)
		if fileName:
			self.qscript = QuircScriptThread(self.irc.connection,self,fileName,RUN_SCRIPT)
			self.qscript.closewindow.connect(self.script_close_window)
			self.qscript.channelmsg.connect(self.script_channel_msg)
			self.qscript.errormsg.connect(self.script_error_msg)
			self.qscript.start()
		else:
			return

	@pyqtSlot(str)
	def script_close_window(self,data):
		self.partChannel(data)

	@pyqtSlot(list)
	def script_channel_msg(self,data):
		channel = data[0]
		msg = data[1]

		if channel.lower() == "server":
			self.serverWindow.writeText(msg)
			return

		if channel.lower() == "console":
			print(msg)
			return
		
		self.writeToChannel(channel,msg)

	@pyqtSlot(list)
	def script_error_msg(self,data):
		line = data[0]
		msg = data[1]

		if line == "0":
			print(f"{msg}")
		else:
			print(f"Line {line}: {msg}")

	def openEditor(self):

		if self.editorWindow == None:
			cw = QMdiSubWindow()
			self.editorWindow = EditorDialog.Dialog(parent=self)
			self.editorSubWindow = cw
			cw.setWidget(self.editorWindow)
			cw.setFont(self.default_font)
			self.MDI.addSubWindow(cw)
			cw.setStyle(QStyleFactory.create(self.qtStyle))
			cw.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))
			self.editorWindow.openDialog()
		else:
			self.editorWindow.openDialog()
		# x = EditorDialog.Dialog(parent=self)
		# x.openDialog()
		self.editorWindow.show()

	def runEditor(self):

		if self.editorWindow == None:
			cw = QMdiSubWindow()
			self.editorWindow = EditorDialog.Dialog(parent=self)
			self.editorSubWindow = cw
			cw.setWidget(self.editorWindow)
			cw.setFont(self.default_font)
			self.MDI.addSubWindow(cw)
			cw.setStyle(QStyleFactory.create(self.qtStyle))
			cw.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))
			self.editorWindow.show()
		else:
			self.editorWindow.show()

		# x = EditorDialog.Dialog(parent=self)
		# x.show()

	def editUserInfo(self):
		x = UserDialog.Dialog(parent=self)
		x.show()

	def joinChannel(self):
		x = JoinDialog.Dialog(parent=self)
		x.show()

	def newNick(self):
		x = NickDialog.Dialog(parent=self)
		x.show()

	def gplLink(self):
		QDesktopServices.openUrl(QUrl("https://www.gnu.org/licenses/gpl-3.0.en.html"))

	def rfc1(self):
		QDesktopServices.openUrl(QUrl("https://tools.ietf.org/html/rfc1459"))

	def rfc2(self):
		QDesktopServices.openUrl(QUrl("https://tools.ietf.org/html/rfc2812"))

	def rfc3(self):
		QDesktopServices.openUrl(QUrl("https://tools.ietf.org/html/rfc2813"))

	def wiki(self):
		QDesktopServices.openUrl(QUrl("https://en.wikipedia.org/wiki/Internet_Relay_Chat"))

	def toggleChannelMenu(self,state):
		if state:
			if not self.useChannelMenu:
				self.useChannelMenu = True
				for c in self.windows:
					c.showMenu()
					c.doResize()
				
		else:
			if self.useChannelMenu:
				self.useChannelMenu = False
				for c in self.windows:
					c.hideMenu()
					c.doResize()
				

	def toggleFloatingMenu(self,state):
		if state:
			if not self.useFloatingMenu:
				self.useFloatingMenu = True
				self.menubar.hide()
				self.floatingMenu.show()
		else:
			if self.useFloatingMenu:
				self.useFloatingMenu = False
				self.menubar.show()
				self.floatingMenu.hide()

	# def toggleAutohide(self,state):
	# 	if state:
	# 		if not self.autoHideMenu:
	# 			self.autoHideMenu = True
	# 			self.menubar.hide()
	# 	else:
	# 		self.autoHideMenu = False

	def toggleWWW(self,state):
		if state:
			self.link_urls = True
		else:
			self.link_urls = False

	def toggleUser(self,state):
		if state:
			self.link_urls = True
		else:
			self.link_urls = False

	def toggleStatus(self,state):
		if state:
			self.STATUS.show()
		else:
			self.STATUS.hide()

	def restartQuirc(self):
		self.RESTART()

	def about(self):
		self.about = AboutDialog(parent=self)
		self.about.show()

	def cascadeWindows(self):
		self.MDI.cascadeSubWindows()

	def tileWindows(self):
		self.MDI.tileSubWindows()

	def exitQuirc(self):
		if self.online:
			self.irc.connection.quit("Quirc IRC Client")
		self.app.quit()

	def showHTML(self,file,title):

		cw = QMdiSubWindow()
		self.html = HTMLDialog.Dialog(parent=self)
		self.htmlSubWindow = cw
		cw.setWidget(self.html)
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create(self.qtStyle))
		cw.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))
		self.html.openHTML(file,title)
		cw.show()

	# def showCMDDocs(self):
	# 	x = HTMLDialog(parent=self)
	# 	x.openHTML(RESOURCE_COMMANDS_DOC_HTML,"QScript Commands")
	# 	x.show()

	def disconnectIRC(self):
		self.online = False
		self.useSSL = False

		#self.irc.connection.disconnect("Quirc IRC Client")
		#self.irc.quit()
		self.irc = None

		self.actConnect.setEnabled(True)
		self.actDisconnect.setEnabled(False)
		self.actJoin.setEnabled(False)
		self.actNick.setEnabled(False)
		self.actRun.setEnabled(False)


		self.clientIsDisconnected()

		# Close all open windows, and set
		# settings to starting defaults
		self.serverSubWindow.close()
		# self.serverWindow.close()
		# self.MDI.removeSubWindow(self.serverSubWindow)
		self.serverSubWindow = None
		self.serverWindow = None
		for c in self.windows:
			c.online = False
			c.subwindow.close()
			self.MDI.removeSubWindow(c.subWindow)
			c.close()
			c = None
		self.users = defaultdict(list)
		self.chatlog = defaultdict(list)
		self.nickname = ''
		self.online = False
		self.host = ''
		self.port = 0
		self.windows = None
		self.windows = []

		self.heart.stop()

		self.actConnect.setVisible(True)
		self.actDisconnect.setVisible(False)
		self.actStored.setVisible(True)

	def ConnectToIrcServer(self,nick,username,realname,host,port,password,use_ssl):
		if int(use_ssl) == 1:
			use_ssl = True
		else:
			use_ssl = False

		if len(password)==0:
			password = None
		if len(username)==0:
			username = None
		if len(realname)==0:
			realname = None

		if len(host)==0:
			self.error_dialog = QErrorMessage()
			self.error_dialog.showMessage("No host entered!")
			return

		if not is_integer(port):
			self.error_dialog = QErrorMessage()
			self.error_dialog.showMessage(f"Invalid port number \"{port}\" entered!")
			return

		self.host = host
		self.port = int(port)

		self.useSSL = use_ssl

		self.irc = None
		del self.irc

		self.irc = QuircClientThread(self,host,int(port),nick,password=password,username=username,ircname=realname,ssl=use_ssl)

		self.irc.connected.connect(self.connected)
		self.irc.pubmsg.connect(self.public_message)
		self.irc.privmsg.connect(self.private_message)
		self.irc.actionmsg.connect(self.action_message)
		self.irc.users.connect(self.userlist)
		self.irc.joined.connect(self.joined)
		self.irc.parted.connect(self.parted)
		self.irc.mynick.connect(self.mynick)
		self.irc.motdmsg.connect(self.motd)
		self.irc.clientjoined.connect(self.clientjoined)
		self.irc.notice.connect(self.notice)
		self.irc.nicklength.connect(self.nicklength)
		self.irc.network.connect(self.network)
		self.irc.disconnected.connect(self.disconnected)
		self.irc.ircerror.connect(self.got_error)

		self.irc.currenttopic.connect(self.got_ctopic)
		self.irc.topicsetter.connect(self.got_stopic)
		self.irc.topic.connect(self.got_topic)

		self.irc.channelinfo.connect(self.got_info)
		self.irc.usermode.connect(self.got_umode)
		self.irc.channelmode.connect(self.got_channelmode)

		#self.irc.dorefresh.connect(self.do_refresh)

		self.irc.start()

		self.serverSubWindow = None
		self.serverWindow = None
		del self.serverSubWindow
		del self.serverWindow
		del self.windows
		self.windows = []
		del self.users
		self.users = defaultdict(list)
		del self.chatlog
		self.chatlog = defaultdict(list)
		del self.nickname
		self.nickname = ''
		del self.online
		self.online = False

		# Spawn server window
		cw = QMdiSubWindow()
		self.serverWindow = ServerWindow(parent=self)
		self.serverSubWindow = cw
		cw.setWidget(self.serverWindow)
		cw.setWindowTitle(f" {self.host}:{int(self.port)}")
		cw.setFont(self.default_font)
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create(self.qtStyle))
		cw.setWindowIcon(QIcon(RESOURCE_ICON_SERVER))

		# cw.setWindowFlags(
		# 	Qt.WindowMinMaxButtonsHint |
		# 	Qt.WindowTitleHint
		# 	)

		self.serverWindow.chatDisplay.setFont(self.default_font)
		self.serverWindow.ircInput.setFont(self.default_font)

		cw.resize(INITIAL_WINDOW_WIDTH,INITIAL_WINDOW_HEIGHT)

		d = system_message(self.system_color,self.background_color,self.system_styles,f"Connecting to {host}:{str(port)}")
		self.serverWindow.writeText(d)

		self.serverWindow.show()

		self.actConnect.setVisible(False)
		self.actDisconnect.setVisible(True)
		self.actJoin.setEnabled(True)
		self.actStored.setVisible(False)


	def storedDialog(self):
		x = ConnectStoredDialog.Dialog()
		connection_info = x.get_connect_information(parent=self)

		if not connection_info:
			# User hit cancel button in dialog
			return

		nick = connection_info[0]
		username = connection_info[1]
		realname = connection_info[2]
		host = connection_info[3]
		port = connection_info[4]
		password = connection_info[5]
		use_ssl = connection_info[6]

		#ConnectToIrcServer(nick,username,realname,host,port,password,use_ssl)
		self.ConnectToIrcServer(nick,username,realname,host,port,password,use_ssl)

	def connectDialog(self):

		x = ConnectDialog.Dialog()
		connection_info = x.get_connect_information(parent=self)

		if not connection_info:
			# User hit cancel button in dialog
			return

		nick = connection_info[0]
		username = connection_info[1]
		realname = connection_info[2]
		host = connection_info[3]
		port = connection_info[4]
		password = connection_info[5]
		use_ssl = connection_info[6]

		#ConnectToIrcServer(nick,username,realname,host,port,password,use_ssl)
		self.ConnectToIrcServer(nick,username,realname,host,port,password,use_ssl)

	@pyqtSlot(list)
	def got_umode(self,data):

		d = system_message(self.system_color,self.background_color,self.system_styles,f"{data[0]} set mode {data[2]} on {data[1]}")
		self.serverWindow.writeText(d)

	@pyqtSlot(list)
	def got_channelmode(self,data):

		user = NickMask(data[0])

		cmode = ''
		for i in data[2]:
			if i[2] == None:
				cmode = cmode + f"{i[0]}{i[1]}"
			else:
				cmode = cmode + f"{i[0]}{i[1]} {i[2]}"
			cmode = cmode + ' '
		cmode.strip()
		d = system_message(self.system_color,self.background_color,self.system_styles,f"{user.nick} set mode {cmode} on {data[1]}")
		self.serverWindow.writeText(d)
		d = system_message(self.system_color,self.background_color,self.system_styles,f"{user.nick} set mode {cmode}")
		self.writeToChannel(data[1],d)

	@pyqtSlot(list)
	def got_info(self,data):
		channel_name = data[CHANNEL_INFO_NAME]
		channel_key = data[CHANNEL_INFO_KEY]
		channel_limit = data[CHANNEL_INFO_LIMIT]
		channel_invite_only = data[CHANNEL_INFO_INVITEONLY]
		channel_allow_external = data[CHANNEL_INFO_ALLOWEXTERNAL]
		channel_topic_locked = data[CHANNEL_INFO_TOPICLOCKED]
		channel_protected = data[CHANNEL_INFO_PROTECTED]
		channel_secret = data[CHANNEL_INFO_SECRET]
		channel_moderated = data[CHANNEL_INFO_MODERATED]
		channel_nocolors = data[CHANNEL_INFO_NOCOLORS]

		for c in self.windows:
			if c.channel == channel_name:
				c.info = data
				c.configureOptions()

	@pyqtSlot(list)
	def got_ctopic(self,data):
		channel = data[0]
		topic = data[1]

		if len(topic)>0:
			d = system_message(self.system_color,self.background_color,self.system_styles,f"Topic for {channel} is: \"{topic}\"")
			self.writeToChannel(channel,d)

		# if len(topic)==0:
		# 	return

		for c in self.windows:
			if c.channel == channel:
				if len(topic)==0:
					c.subWindow.setWindowTitle(f" {channel}")
					c.topic = ''
				else:
					c.subWindow.setWindowTitle(f" {channel}  \"{topic}\"")
					c.topic = topic

	@pyqtSlot(list)
	def got_stopic(self,data):
		channel = data[0]
		nick = data[1]

		if self.link_users:
			nick = f"<a href=\"{nick}\"><span style=\"font-style: normal; text-decoration: none; color: {self.system_color};\">{nick}</span></a>"

		if self.topic:
			if len(self.topic)>0:
				d = system_message(self.system_color,self.background_color,self.system_styles,f"Topic for {channel} set by {nick}")
				self.writeToChannel(channel,d)

	@pyqtSlot(list)
	def got_topic(self,data):
		channel = data[0]
		topic = data[1]
		nick = data[2]
		hostmask = data[3]

		if self.link_users:
			nick = f"<a href=\"{nick}\"><span style=\"font-style: normal; text-decoration: none;  color: {self.system_color};\">{nick}</span></a>"

		if len(topic)>0:
			d = system_message(self.system_color,self.background_color,self.system_styles,f"{nick}({hostmask}) set topic to \"{topic}\"")
			self.writeToChannel(channel,d)

		for c in self.windows:
			if c.channel == channel:
				if len(topic)==0:
					c.subWindow.setWindowTitle(f" {channel}")
					c.topic = ''
				else:
					c.subWindow.setWindowTitle(f" {channel}  \"{topic}\"")
					c.topic = topic

	@pyqtSlot(list)
	def got_error(self,data):
		err_type = data[0]
		err_target = data[1]
		err_msg = data[2]

		if err_type == "join":
			# join channel error
			d = system_message(self.error_color,self.background_color,self.system_styles,f"Can't join {err_target}: {err_msg}")
			self.writeToChannel(err_target,d)
		elif err_type == "channel":
			# channel error
			d = system_message(self.error_color,self.background_color,self.system_styles,f"{err_target} error: {err_msg}")
			self.writeToChannel(err_target,d)
		else:
			if self.skipNextError:
				self.skipNextError = False
				return
			# everything else
			d = system_message(self.error_color,self.background_color,self.system_styles,f"Error: {err_msg}")
			self.writeToAllChannels(d)

	@pyqtSlot()
	def disconnected(self):
		# pointless
		pass

	@pyqtSlot(str)
	def clientjoined(self,data):
		channel = data

		d = system_message(self.system_color,self.background_color,self.system_styles,f"Joined {channel}.")
		self.writeToChannel(channel,d)

	def partChannel(self,channel):
		for c in self.windows:
			if c.channel == channel:
				c.subWindow.close()
				c.close()
				return

	def writeToChannel(self,channel,data):
		for c in self.windows:
			if c.channel == channel:
				c.writeText(data)
				return
		cw = QMdiSubWindow()
		chan = ChannelWindow(channel,self.nickname,self.irc.connection,cw,parent=self)
		cw.setWidget(chan)
		cw.setWindowTitle(f" {channel}")
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create(self.qtStyle))
		chan.subWindow = cw
		self.windows.append(chan)

		chan.chatDisplay.setFont(self.default_font)
		chan.ircInput.setFont(self.default_font)
		chan.userList.setFont(self.userlist_font)
		chan.setStyleSheet(self.child_qss)

		if not self.useChannelMenu:
			chan.hideMenu()

		cw.setWindowIcon(QIcon(RESOURCE_ICON_HASH))

		chan.writeText(data)
		cw.resize(INITIAL_WINDOW_WIDTH,INITIAL_WINDOW_HEIGHT)
		cw.show()

	def raiseOrCreateUserWindow(self,channel):
		for c in self.windows:
			if c.channel == channel:
				self.MDI.setActiveSubWindow(c.subWindow)
				return
		cw = QMdiSubWindow()
		chan = UserWindow(channel,self.nickname,self.irc.connection,cw,parent=self)
		cw.setWidget(chan)
		cw.setWindowTitle(f" {channel}")
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create(self.qtStyle))
		chan.subWindow = cw
		self.windows.append(chan)

		chan.chatDisplay.setFont(self.default_font)
		chan.ircInput.setFont(self.default_font)
		chan.setStyleSheet(self.child_qss)

		cw.setWindowIcon(QIcon(RESOURCE_ICON_USER))

		d = system_message(self.system_color,self.background_color,self.system_styles,f"Chatting with {channel}.")
		chan.writeText(d)
		cw.resize(INITIAL_WINDOW_WIDTH,INITIAL_WINDOW_HEIGHT)
		cw.show()


	def writeToUser(self,channel,data):
		for c in self.windows:
			if c.channel == channel:
				c.writeText(data)
				return
		cw = QMdiSubWindow()
		chan = UserWindow(channel,self.nickname,self.irc.connection,cw,parent=self)
		cw.setWidget(chan)
		cw.setWindowTitle(f" {channel}")
		self.MDI.addSubWindow(cw)
		cw.setStyle(QStyleFactory.create(self.qtStyle))
		chan.subWindow = cw
		self.windows.append(chan)

		chan.chatDisplay.setFont(self.default_font)
		chan.ircInput.setFont(self.default_font)
		chan.setStyleSheet(self.child_qss)

		cw.setWindowIcon(QIcon(RESOURCE_ICON_USER))

		chan.writeText(data)
		cw.resize(INITIAL_WINDOW_WIDTH,INITIAL_WINDOW_HEIGHT)
		cw.show()

	def writeToAllChannels(self,data):
		for c in self.windows:
			c.writeText(data)
		self.serverWindow.writeText(data)

	@pyqtSlot(str)
	def nicklength(self,data):
		self.maxnicklength = int(data)

	@pyqtSlot(str)
	def network(self,data):
		self.networkname = data

	@pyqtSlot(str)
	def mynick(self,data):
		self.nickname = data

		for c in self.windows:
			c.nickname = data

	@pyqtSlot(list)
	def motd(self,data):

		m = "<br>".join(data)
		d = chat_message(self.motd_color,self.background_color,self.chat_color,"MOTD",m,self.maxnicklength)
		self.serverWindow.writeText(d)

	def refresh_all_users(self):
		for c in self.windows:
			if c.is_irc_channel:
				self.irc.refresh_users(c.channel)

	@pyqtSlot(list)
	def parted(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		msg = data[3]

		if self.link_users:
			nick = f"<a href=\"{nick}\"><span style=\"font-style: normal; text-decoration: none;  color: {self.system_color};\">{nick}</span></a>"

		d = system_message(self.system_color,self.background_color,self.system_styles,f"{nick} left {channel}.")
		self.writeToChannel(channel,d)
		self.irc.refresh_users(channel)

	@pyqtSlot(list)
	def joined(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]

		if self.link_users:
			nick = f"<a href=\"{nick}\"><span style=\"font-style: normal; text-decoration: none;  color: {self.system_color};\">{nick}</span></a>"

		d = system_message(self.system_color,self.background_color,self.system_styles,f"{nick} joined {channel}.")
		self.writeToChannel(channel,d)
		self.irc.refresh_users(channel)

	@pyqtSlot()
	def connected(self):
		self.online = True

		if self.useSSL:
			self.clientIsUsingSSL()
		else:
			self.clientIsNotUsingSSL()

		self.serverWindow.setIRCConnection(self.irc.connection)

		self.actConnect.setEnabled(False)
		self.actDisconnect.setEnabled(True)
		self.actNick.setEnabled(True)
		self.actRun.setEnabled(True)
		self.actStored.setVisible(False)

		self.uptime = 0
		self.heart = Heartbeat(self)
		self.heart.beat.connect(self.tick)
		self.heart.start()

		self.irc.connection.join("#quirc")

	@pyqtSlot(list)
	def public_message(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if self.link_users:
			d = chat_message_link(self.username_color,self.background_color,self.chat_color,nick,message,self.maxnicklength,self.link_color)
		else:
			d = chat_message(self.username_color,self.background_color,self.chat_color,nick,message,self.maxnicklength)
		self.writeToChannel(channel,d)

	@pyqtSlot(list)
	def private_message(self,data):
		target = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if self.link_users:
			d = chat_message_link(self.username_color,self.background_color,self.chat_color,nick,message,self.maxnicklength,self.link_color)
		else:
			d = chat_message(self.username_color,self.background_color,self.chat_color,nick,message,self.maxnicklength)
			

		self.writeToUser(nick,d)

	@pyqtSlot(list)
	def action_message(self,data):
		channel = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if self.link_users:
			d = action_message_link(self.action_color,self.background_color,nick,message,self.link_color)
		else:
			d = action_message(self.action_color,self.background_color,nick,message)
		self.writeToChannel(channel,d)

	@pyqtSlot(list)
	def notice(self,data):
		target = data[0]
		nick = data[1]
		hostmask = data[2]
		message = data[3]

		if nick == "SERVER":
			if hostmask == "SERVER":
				nick = self.host
				hostmask = self.host
		else:
			if self.link_users:
				nick = f"<a href=\"{nick}\"><span style=\"font-style: normal; text-decoration: none;  color: {self.notice_color};\">{nick}</span></a>"

		if len(target)>1:
			if target[0] == '#':
				d = chat_message(self.notice_color,self.background_color,self.chat_color,nick,message,self.maxnicklength)
				self.writeToChannel(target,d)
				self.serverWindow.writeText(d)
			elif target[0] == '&':
				d = chat_message(self.notice_color,self.background_color,self.chat_color,nick,message,self.maxnicklength)
				self.writeToChannel(target,d)
				self.serverWindow.writeText(d)
			else:
				d = chat_message(self.notice_color,self.background_color,self.chat_color,nick,message,self.maxnicklength)
				self.writeToAllChannels(d)
				#self.serverWindow.writeText(d)

	@pyqtSlot(str,list)
	def userlist(self,channel,users):

		self.users[channel] = users

		nicklist = []
		for n in users:
			nu = NickMask(n)
			nicklist.append(nu.nick)
		for c in self.windows:
			if c.channel == channel:
				c.setUsers(nicklist)

	def closeEvent(self, event):
		self.app.quit()

	def removeChannel(self,channel):
		cc = []
		for c in self.windows:
			if c.channel == channel:
				continue
			cc.append(c)
		self.windows = cc

class Heartbeat(QThread):

	beat = pyqtSignal()

	def __init__(self,parent=None):
		super(Heartbeat, self).__init__(parent)
		self.threadactive = True

	def run(self):
		while self.threadactive:
			time.sleep(1)
			self.beat.emit()

	def stop(self):
		self.threadactive = False
		self.wait()
