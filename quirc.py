
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
import functools
from datetime import datetime

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

from quirc import connect,connectSSL
from quirc.common import *

import quirc.dialogs.connect as ConnectDialog
import quirc.dialogs.join as JoinDialog
import quirc.dialogs.nick as NickDialog
import quirc.dialogs.networks as NetworkDialog
import quirc.dialogs.about as AboutDialog

import quirc.windows.channel as ChatWindow

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

class GUI(QMainWindow):

	def closeEvent(self, event):
		self.app.quit()

	def handleUserInput(self,user,data):

		return False

	def handleChannelInput(self,channel,data):
		# If a command is handled, return True

		return False

	def clientIsConnecting(self):
		self.status_icon.setPixmap(self.DISCONNECTED_ICON)
		self.status_text.setText(f"Connecting to {self.host}:{self.port}...")

	def clientIsConnected(self):
		self.status_icon.setPixmap(self.CONNECTED_ICON)
		self.status_text.setText(f"Connected to {self.host}:{self.port} as \"{self.nickname}\"")

	def clientIsDisconnected(self):
		self.status_icon.setPixmap(self.DISCONNECTED_ICON)
		self.status_text.setText("Disconnected")

	def __init__(self,app,parent=None):
		super(GUI, self).__init__(parent)

		self.parent = parent
		self.app = app

		self.font = QFont(QUIRC_FONT,QUIRC_FONT_SIZE)
		self.fontBold = QFont(QUIRC_FONT,QUIRC_FONT_SIZE,QFont.Bold)

		app.setFont(self.font)

		self.irc = None
		self.nickname = ""

		self.is_connected = False

		self.server = ""

		self.windows = {}

		self.keepConnectionAlive = True

		self.autojoin = []

		self.colors = load_colors()

		self.setWindowTitle(f"{APPLICATION_NAME}")
		self.setWindowIcon(QIcon(QUIRC_ICON))

		self.MDI = QMdiArea()
		self.setCentralWidget(self.MDI)

		pix = QPixmap(MDI_BACKGROUND)
		self.backgroundBrush = QBrush(pix)
		self.MDI.setBackground(self.backgroundBrush)

		# Status bar
		self.CONNECTED_ICON = QIcon(CONNECTED_ICON).pixmap(16,16)
		self.DISCONNECTED_ICON = QIcon(DISCONNECTED_ICON).pixmap(16,16)
		self.status = self.statusBar()


		self.status_icon = QLabel()
		self.status_icon.setPixmap(self.DISCONNECTED_ICON)
		self.status_text = QLabel("Disconnected")
		self.status.addPermanentWidget(self.status_icon,0)
		self.status.addPermanentWidget(self.status_text,1)

		self.status.setFont(self.fontBold)

		# Menus

		self.menubar = self.menuBar()

		# Quirc Menu

		ircMenu = self.menubar.addMenu(f"{APPLICATION_NAME}")

		self.actConnect = QAction(QIcon(SERVER_ICON),"Connect to Server",self)
		self.actConnect.triggered.connect(self.doConnectDialog)
		if QUIRC_HOTKEY_CONNECT != None: self.actConnect.setShortcut(QUIRC_HOTKEY_CONNECT)
		ircMenu.addAction(self.actConnect)

		self.actNetwork = QAction(QIcon(NETWORK_ICON),"Connect to Network",self)
		self.actNetwork.triggered.connect(self.doNetworkDialog)
		if QUIRC_HOTKEY_NETWORK != None: self.actNetwork.setShortcut(QUIRC_HOTKEY_NETWORK)
		ircMenu.addAction(self.actNetwork)

		self.actDisconnect = QAction(QIcon(DISCONNECTED_ICON),"Disconnect",self)
		self.actDisconnect.triggered.connect(self.doDisconnect)
		if QUIRC_HOTKEY_DISCONNECT != None: self.actDisconnect.setShortcut(QUIRC_HOTKEY_DISCONNECT)
		ircMenu.addAction(self.actDisconnect)
		self.actDisconnect.setEnabled(False)

		ircMenu.addSeparator()

		self.optAlive = QAction(QIcon(HEARTBEAT_ON_ICON),"Keep alive on",self)
		self.optAlive.triggered.connect(self.toggleAlive)
		ircMenu.addAction(self.optAlive)
		self.optAlive.setEnabled(False)

		ircMenu.addSeparator()

		self.actNick = QAction(QIcon(USER_ICON),"New Nickname",self)
		self.actNick.triggered.connect(self.doNickDialog)
		if QUIRC_HOTKEY_NICK != None: self.actNick.setShortcut(QUIRC_HOTKEY_NICK)
		ircMenu.addAction(self.actNick)
		self.actNick.setEnabled(False)

		self.actJoin = QAction(QIcon(CHANNEL_ICON),"Join Channel",self)
		self.actJoin.triggered.connect(self.doJoinDialog)
		if QUIRC_HOTKEY_JOIN != None: self.actJoin.setShortcut(QUIRC_HOTKEY_JOIN)
		ircMenu.addAction(self.actJoin)
		self.actJoin.setEnabled(False)

		ircMenu.addSeparator()

		self.actQuit = QAction(QIcon(EXIT_ICON),"Exit",self)
		self.actQuit.triggered.connect(self.close)
		if QUIRC_HOTKEY_QUIT != None: self.actQuit.setShortcut(QUIRC_HOTKEY_QUIT)
		ircMenu.addAction(self.actQuit)

		# Windows Menu

		self.winMenu = self.menubar.addMenu("Windows")

		self.rebuildWindowMenu()

		self.updateActiveChild(self.MDI.activeSubWindow())
		# install signal handlers
		self.MDI.subWindowActivated.connect(self.updateActiveChild)

		# Help Menu

		helpMenu = self.menubar.addMenu("Help")

		self.actAbout = QAction(QIcon(ABOUT_ICON),f"About {APPLICATION_NAME}",self)
		self.actAbout.triggered.connect(self.doAbout)
		helpMenu.addAction(self.actAbout)

	def setClient(self,obj):
		self.irc = obj
		self.nickname = obj.nickname

	# Methods

	def toggleAlive(self):
		if self.keepConnectionAlive:
			self.keepConnectionAlive = False
			self.optAlive.setIcon(QIcon(HEARTBEAT_OFF_ICON))
			self.optAlive.setText("Keep alive off")
			self.irc.stopHeartbeat()
		else:
			self.keepConnectionAlive = True
			self.optAlive.setIcon(QIcon(HEARTBEAT_ON_ICON))
			self.optAlive.setText("Keep alive on")
			self.irc.startHeartbeat()

	def raiseWindow(self,w):

		self.windows[w].window.showNormal()
		self.windows[w].window.userTextInput.setFocus()

	def rebuildWindowMenu(self):

		self.winMenu.clear()

		actCascade = QAction(QIcon(CASCADE_ICON),"Cascade Windows",self)
		actCascade.triggered.connect(self.cascadeWindows)
		self.winMenu.addAction(actCascade)

		actTile = QAction(QIcon(TILE_ICON),"Tile Windows",self)
		actTile.triggered.connect(self.tileWindows)
		self.winMenu.addAction(actTile)

		self.winMenu.addSeparator()

		for w in self.windows:

			if w==self.server:
				self.winMenu.addAction(QIcon(SERVER_ICON),w, functools.partial(self.raiseWindow, w))
			elif '#' in w:
				self.winMenu.addAction(QIcon(CHANNEL_ICON),w, functools.partial(self.raiseWindow, w))
			else:
				self.winMenu.addAction(QIcon(USER_ICON),w, functools.partial(self.raiseWindow, w))

	def doDisconnect(self):
		if self.irc != None:
			self.irc.quit(f"{APPLICATION_NAME} {APPLICATION_VERSION}")

			for w in self.windows:
				self.windows[w].subwindow.close()

			self.windows = {}

	def writeToAllWindows(self,txt):
		for w in self.windows:
			self.windows[w].window.writeText(txt)

	def updateActiveChild(self,subWindow):
		try:
			w = subWindow.windowTitle()
		except:
			return
		w = w.strip()
		if ' ' in w:
			p = w.split(' ')
			if len(p)>=1:
				w = p[0]
		for x in self.winMenu.actions():
			t = x.text()
			if t.isspace() or len(t)==0: continue
			if t=="Tile Windows": continue
			if t=="Cascade Windows": continue
			t = t.strip()
			if ' ' in t:
				p = t.split(' ')
				if len(p)>=1:
					t = p[0]

			if w == t:
				# found the active window menu item
				f = x.font()
				f.setBold(True)
				x.setFont(f)
				continue

			f = x.font()
			f.setBold(False)
			x.setFont(f)

	# Dialogs

	def doNickDialog(self):

		x = NickDialog.Dialog()
		newnick = x.get_nick_information(parent=self)

		# User cancled dialog
		if not newnick: return

		if newnick.isspace() or len(newnick)==0:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(QUIRC_ICON))
			msg.setIcon(QMessageBox.Critical)
			msg.setText("No nick entered")
			#msg.setInformativeText(f"No channel entered")
			msg.setWindowTitle("Error")
			msg.exec_()
			return

		self.irc.setNick(newnick)
		self.nickname = newnick

		self.clientIsConnected()

		# self.sendLine(f"NAMES {channel}")
		for w in self.windows:
			if w == self.server: continue
			self.irc.sendLine(f"NAMES {w}")

	def doJoinDialog(self):

		x = JoinDialog.Dialog()
		channel_info = x.get_channel_information(parent=self)

		# User cancled dialog
		if not channel_info: return

		channel = channel_info[0]
		password = channel_info[1]

		if channel.isspace() or len(channel)==0:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(QUIRC_ICON))
			msg.setIcon(QMessageBox.Critical)
			msg.setText("No channel entered")
			#msg.setInformativeText(f"No channel entered")
			msg.setWindowTitle("Error")
			msg.exec_()
			return

		if password.isspace() or len(password)==0:
			self.irc.join(channel)
		else:
			self.irc.join(channel,password)
		
	def doConnectDialog(self):

		x = ConnectDialog.Dialog()
		connection_info = x.get_connect_information(parent=self)

		# User cancled dialog
		if not connection_info: return

		nick = connection_info[0]
		username = connection_info[1]
		realname = connection_info[2]
		host = connection_info[3]
		port = connection_info[4]
		password = connection_info[5]
		use_ssl = connection_info[6]

		# Sanity check
		errs = []
		if len(nick)==0: errs.append("nickname not entered")
		if len(username)==0: errs.append("username not entered")
		if len(realname)==0: errs.append("real name not entered")
		if len(host)==0: errs.append("host not entered")
		if len(port)==0: errs.append("port not entered")
		if not is_integer(port):
			if port!= "": errs.append(f"invalid port \"{port}\"")
		if len(errs)>0:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(QUIRC_ICON))
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Missing or Invalid Input")
			es = ""
			for e in errs: es = es + f"<li>{e}</li>"
			msg.setInformativeText(f"<ul>{es}</ul>")
			msg.setWindowTitle("Can't connect to IRC")
			msg.exec_()
			return

		# Save server information
		if use_ssl==1:
			save_last_server( host, port, password, True )
		else:
			save_last_server( host, port, password, False )

		# Save user information
		user = {
			"nick": str(nick),
			"username": str(username),
			"realname": str(realname)
		}
		save_user(user)

		self.host = host
		self.port = port
		self.server = f"{self.host}:{self.port}"

		# If we're already connected to a server, disconnect
		if self.is_connected:
			self.doDisconnect()

		self.clientIsConnecting()

		self.nickname = nick

		if use_ssl == 1:
			if password != '':
				connectSSL(host,int(port),nick,username,realname,self,password)
			else:
				connectSSL(host,int(port),nick,username,realname,self,None)
		else:
			if password != '':
				connect(host,int(port),nick,username,realname,self,password)
			else:
				connect(host,int(port),nick,username,realname,self,None)

	def doNetworkDialog(self):

		x = NetworkDialog.Dialog()
		connection_info = x.get_connect_information(parent=self)

		# User cancled dialog
		if not connection_info: return

		nick = connection_info[0]
		username = connection_info[1]
		realname = connection_info[2]
		host = connection_info[3]
		port = connection_info[4]
		password = connection_info[5]
		use_ssl = connection_info[6]

		# Sanity check
		errs = []
		if len(nick)==0: errs.append("nickname not entered")
		if len(username)==0: errs.append("username not entered")
		if len(realname)==0: errs.append("real name not entered")
		if len(host)==0: errs.append("host not entered")
		if len(port)==0: errs.append("port not entered")
		if not is_integer(port):
			if port!= "": errs.append(f"invalid port \"{port}\"")
		if len(errs)>0:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(QUIRC_ICON))
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Missing or Invalid Input")
			es = ""
			for e in errs: es = es + f"<li>{e}</li>"
			msg.setInformativeText(f"<ul>{es}</ul>")
			msg.setWindowTitle("Can't connect to IRC")
			msg.exec_()
			return

		# Save server information
		if use_ssl==1:
			save_last_server( host, port, password, True )
		else:
			save_last_server( host, port, password, False )

		# Save user information
		user = {
			"nick": str(nick),
			"username": str(username),
			"realname": str(realname)
		}
		save_user(user)

		self.host = host
		self.port = port
		self.server = f"{self.host}:{self.port}"

		# If we're already connected to a server, disconnect
		if self.is_connected:
			self.doDisconnect()

		self.clientIsConnecting()

		self.nickname = nick

		if use_ssl == 1:
			if password != '':
				connectSSL(host,int(port),nick,username,realname,self,password)
			else:
				connectSSL(host,int(port),nick,username,realname,self,None)
		else:
			if password != '':
				connect(host,int(port),nick,username,realname,self,password)
			else:
				connect(host,int(port),nick,username,realname,self,None)

	# Windows

	def printToActiveWindow(self,txt):
		activeSubWindow = self.MDI.activeSubWindow()
		if activeSubWindow:
			x = activeSubWindow.widget()
			x.writeText(txt)

	def doAbout(self):
		x = QMdiSubWindow()
		x.setWidget(AboutDialog.Dialog())
		x.setWindowFlags(
			Qt.WindowCloseButtonHint |
			Qt.WindowTitleHint )
		self.MDI.addSubWindow(x)
		x.show()

	def newChatWindow(self,channel,isserver=False):
		newChan = Channel(channel)
		newChan.setSubwindow(QMdiSubWindow())
		newChan.setWindow(ChatWindow.Viewer(channel,self.irc,self,isserver))
		newChan.subwindow.setWidget(newChan.window)
		self.MDI.addSubWindow(newChan.subwindow)

		newChan.subwindow.setWindowFlags(
			Qt.WindowMinimizeButtonHint |
			Qt.WindowMaximizeButtonHint |
			Qt.WindowTitleHint )

		newChan.subwindow.resize(INITIAL_WINDOW_SIZE_WIDTH,INITIAL_WINDOW_SIZE_HEIGHT)

		#newChan.window.show()
		newChan.subwindow.show()

		self.windows[channel] = newChan

		self.rebuildWindowMenu()

	def cascadeWindows(self):
		self.MDI.cascadeSubWindows()

	def tileWindows(self):
		self.MDI.tileSubWindows()

	def getTimestamp(self):
		return datetime.timestamp(datetime.now())

	# IRC events

	def whois(self,whois):
		t = makeWhoisPretty(whois)
		d = whois_display(t,MAX_USERNAME_SIZE)
		self.printToActiveWindow(d)
		#self.windows[self.server].window.writeText(d)

	def joinedChannel(self,channel):
		self.newChatWindow(channel)
		d = system_display(f"Joined {channel}")
		self.windows[channel].window.writeText(d)
		self.windows[self.server].window.writeText(d)
		self.windows[channel].chat.append(f"{self.getTimestamp()} Joined {channel}")

	def connected(self):
		self.clientIsConnected()
		self.actDisconnect.setEnabled(True)
		self.actConnect.setEnabled(False)
		self.actNetwork.setEnabled(False)
		self.actJoin.setEnabled(True)
		self.actNick.setEnabled(True)
		self.optAlive.setEnabled(True)

		self.newChatWindow(self.server,True)
		d = system_display(f"Connected to {self.server}")
		self.windows[self.server].window.writeText(d)

		self.is_connected = True

	def disconnected(self):
		self.clientIsDisconnected()
		self.actDisconnect.setEnabled(False)
		self.actConnect.setEnabled(True)
		self.actNetwork.setEnabled(True)
		self.actJoin.setEnabled(False)
		self.actNick.setEnabled(False)
		self.optAlive.setEnabled(False)

		self.doDisconnect()

		self.is_connected = False

	def registered(self):
		d = system_display(f"Registered with {self.server}")
		self.windows[self.server].window.writeText(d)

		if self.keepConnectionAlive:
			self.irc.startHeartbeat()

		# Autojoin channels
		self.autojoin = get_autojoins()
		for c in self.autojoin:
			p = c.split("/")
			if len(p)==2:
				self.irc.join(p[0],p[1])
			else:
				self.irc.join(c)

	def privatemsg(self,user,msg):
		#print(f"{user}: {msg}")

		p = user.split('!')
		if len(p)==2:
			nick = p[0]
			hostmask = p[1]
		else:
			nick = user
			hostmask = ''

		if nick in self.windows:
			d = chat_display(nick,msg,MAX_USERNAME_SIZE)
			self.windows[nick].window.writeText(d)
			# self.windows[user].window.writeText(f"{nick}: {msg}")
			self.windows[nick].chat.append(f"{self.getTimestamp()} PRIVATE {user}: {msg}")
		else:
			self.newChatWindow(nick)
			#self.windows[user].window.writeText(f"{nick}: {msg}")
			d = chat_display(nick,msg,MAX_USERNAME_SIZE)
			self.windows[nick].window.writeText(d)
			self.windows[nick].chat.append(f"{self.getTimestamp()} PRIVATE {user}: {msg}")

	def publicmsg(self,user,target,msg):
		#print(f"{target} {user}: {msg}")

		self.raiseWindow(target)

		p = user.split('!')
		if len(p)==2:
			nick = p[0]
			hostmask = p[1]
		else:
			nick = user
			hostmask = ''

		if target in self.windows:
			#self.windows[target].window.writeText(f"{nick}: {msg}")
			d = chat_display(nick,msg,MAX_USERNAME_SIZE)
			self.windows[target].window.writeText(d)
			self.windows[target].chat.append(f"{self.getTimestamp()} {target} {user}: {msg}")

		# for w in self.windows:
		# 	self.MDI.setActiveSubWindow(self.windows[w].subwindow)

	def notice(self,user,target,msg):
		
		p = user.split('!')
		if len(p)==2:
			nick = p[0]
			hostmask = p[1]
		else:
			nick = user
			hostmask = ''

		if target in self.windows:
			#self.windows[target].window.writeText(f"{nick}: {msg}")
			d = notice_display(nick,msg,MAX_USERNAME_SIZE)
			self.windows[target].window.writeText(d)
			self.windows[target].chat.append(f"{self.getTimestamp()} NOTICE {target} {user}: {msg}")

		if target != self.nickname or target != '*':
			d = notice_display(nick,f"{target}: {msg}",MAX_USERNAME_SIZE)
		else:
			d = notice_display(nick,msg,MAX_USERNAME_SIZE)
		self.windows[self.server].window.writeText(d)

	def motd(self,motd):
		x = "<br>\n".join(motd)
		d = motd_display(x,MAX_USERNAME_SIZE)
		self.windows[self.server].window.writeText(d)

	def mode(self,user,channel,set,modes,args):
		p = user.split('!')
		if len(p)==2:
			user = p[0]
		if set:
			pom = "+"
		else:
			pom = "-"
		c = []
		for a in args:
			if a==None: continue
			c.append(a)
		args = c
		if len(args)>0:
			msg = f"{user} set mode {pom}{modes} {' '.join(args)}"
		else:
			msg = f"{user} set mode {pom}{modes}"

		d = system_display(msg)
		if channel in self.windows:
			self.windows[channel].window.writeText(d)
			self.windows[channel].chat.append(f"{self.getTimestamp()} {msg}")
		self.windows[self.server].window.writeText(d)


	def modemsg(self,user,channel,txt):
		d = system_display(txt)
		self.windows[channel].window.writeText(d)
		self.windows[self.server].window.writeText(d)
		self.windows[channel].chat.append(f"{self.getTimestamp()} {txt}")

	def joined(self,user,channel):
		if channel in self.windows:
			q = user.split('!')
			if len(q) == 2:
				user = q[0]

			d = system_display(f"{user} joined {channel}")
			self.windows[channel].window.writeText(d)
			self.windows[self.server].window.writeText(d)
			self.windows[channel].chat.append(f"{self.getTimestamp()} {user} joined {channel}")

	def parted(self,user,channel):
		if channel in self.windows:
			q = user.split('!')
			if len(q) == 2:
				user = q[0]

			d = system_display(f"{user} left {channel}")
			self.windows[channel].window.writeText(d)
			self.windows[self.server].window.writeText(d)
			self.windows[channel].chat.append(f"{self.getTimestamp()} {user} left {channel}")

	def rename(self,oldnick,newnick):
		
		present = []
		for w in self.windows:

			for u in self.windows[w].users:
				u = u.replace("@","",1)
				if u == oldnick or u == newnick:
					present.append(self.windows[w].channelName())

		for p in present:
			self.irc.sendLine(f"NAMES {p}")
			d = system_display(f"{oldnick} is now known as {newnick}")
			self.windows[p].window.writeText(d)
			self.windows[p].chat.append(f"{self.getTimestamp()} {oldnick} is now known as {newnick}")

	def topic(self,user,channel,topic):
		if channel in self.windows:
			if topic.isspace() or topic=="":
				self.windows[channel].window.clearTopic()
				self.windows[channel].window.topic = topic
			else:
				self.windows[channel].window.setTopic(topic)
				d = system_display(f"{user} set the topic to {topic}")
				self.windows[channel].window.writeText(d)
				self.windows[channel].chat.append(f"{self.getTimestamp()} {user} set the topic to {topic}")

	def users(self,channel,userlist):
		
		if channel in self.windows:
			self.windows[channel].window.setUserList(userlist)
			self.windows[channel].setUsers(userlist)

	def quit(self,user,msg):

		q = user.split('!')
		if len(q) == 2:
			user = q[0]
		
		present = []
		for w in self.windows:

			for u in self.windows[w].users:
				u = u.replace("@","",1)
				if u == user:
					present.append(self.windows[w].channelName())

		for p in present:
			self.irc.sendLine(f"NAMES {p}")
			if msg == "":
				d = system_display(f"{user} disconnected from IRC")
				self.windows[p].window.writeText(d)
				self.windows[self.server].window.writeText(d)
				self.windows[p].chat.append(f"{self.getTimestamp()} {user} disconnected from IRC")
			else:
				d = system_display(f"{user} disconnected from IRC ({msg})")
				self.windows[p].window.writeText(d)
				self.windows[self.server].window.writeText(d)
				self.windows[p].chat.append(f"{self.getTimestamp()} {user} disconnected from IRC ({msg})")


	def action(self,user,channel,msg):
		p = user.split("!")
		if len(p) == 2:
			user = p[0]

		if channel in self.windows:
			d = action_display(user,msg)
			self.windows[channel].window.writeText(d)
			self.windows[channel].chat.append(f"{self.getTimestamp()} ACTION {channel} {user} {msg}")


	def kick(self,kicker,kickee,channel,message):
		if len(message)>0:
			d = system_display(f"{kicker} kicked {kickee} from {channel}: {message}")
			self.windows[channel].chat.append(f"{self.getTimestamp()} {kicker} kicked {kickee} from {channel}: {message}")
		else:
			d = system_display(f"{kicker} kicked {kickee} from {channel}")
			self.windows[channel].chat.append(f"{self.getTimestamp()} {kicker} kicked {kickee} from {channel}")
		self.windows[channel].window.writeText(d)


	def kicked(self,kicker,channel,message):
		
		# remove channel window
		cleaned = {}
		for w in self.windows:
			if w == channel:
				self.windows[w].subwindow.close()
				self.windows[w] = None
			else:
				cleaned[w] = self.windows[w]

		self.windows = cleaned
		self.rebuildWindowMenu()

		if len(message)>0:
			d = system_display(f"{kicker} kicked you from {channel}: {message}")
		else:
			d = system_display(f"{kicker} kicked you from {channel}")
		self.windows[self.server].window.writeText(d)

	def ircerror(self,data):
		d = error_display(data)
		self.printToActiveWindow(d)
		self.windows[self.server].window.writeText(d)

if __name__ == '__main__':

	app = QApplication(sys.argv)
	app.setStyle('Windows')

	ircform = GUI(app)
	ircform.show()

	#connect("localhost",6667,"bob","bob","bob",ircform)

	reactor.run()
