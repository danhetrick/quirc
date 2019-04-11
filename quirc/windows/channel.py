
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
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from irc.client import NickMask

from quirc.common import *

class Viewer(QMainWindow):

	def changeEvent(self, event):

		for w in self.parent.windows:
			if self.parent.windows[w].name == self.name:
				if event.type() == QEvent.WindowStateChange:
					if event.oldState() and Qt.WindowMinimized:
						self.parent.windows[w].minimized = True
					elif event.oldState() == Qt.WindowNoState or self.windowState() == Qt.WindowMaximized:
						self.parent.windows[w].minimized = False

	def __init__(self,name,client,parent=None,isserver=False):
		super(Viewer, self).__init__(parent)

		self.name = name
		self.client = client
		self.parent = parent

		self.isserver = isserver

		if len(name)>0 and name[0]=='#':
			self.is_channel = True
		else:
			self.is_channel = False

		self.irc = parent.irc

		self.font = QFont(QUIRC_FONT,QUIRC_FONT_SIZE)
		self.fontBold = QFont(QUIRC_FONT,QUIRC_FONT_SIZE,QFont.Bold)
		self.fontItalic = QFont(QUIRC_FONT,QUIRC_FONT_SIZE,QFont.Normal,True)
		self.fontBoldItalic = QFont(QUIRC_FONT,QUIRC_FONT_SIZE,QFont.Bold,True)

		self.userlist = []

		self.users = []

		self.banned = []

		self.is_op = False
		self.is_voiced = False

		self.topic = ''

		self.history_buffer = []
		self.history_buffer_pointer = 0
		self.history_buffer_max = 20

		self.buildInterface()

	def setServerIcon(self):
		self.setWindowIcon(QIcon(QUIRC_ICON))

	def doPart(self):

		cleaned = {}
		for w in self.parent.windows:
			if w == self.name:
				self.parent.windows[w].subwindow.close()
				self.parent.windows[w] = None
			else:
				cleaned[w] = self.parent.windows[w]

		self.parent.windows = cleaned
		
		self.irc.part(self.name)

		self.parent.rebuildWindowMenu()

	def doLeave(self):

		cleaned = {}
		for w in self.parent.windows:
			if w == self.name:
				self.parent.windows[w].subwindow.close()
				self.parent.windows[w] = None
			else:
				cleaned[w] = self.parent.windows[w]

		self.parent.windows = cleaned

		self.parent.rebuildWindowMenu()

	def doUserWhois(self):

		self.parent.irc.whois(self.name)

	def doTopicCopy(self):
		cb = QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(f"{self.topic}", mode=cb.Clipboard)

	def doUserCopy(self):
		users = self.parent.windows[self.name].users

		cb = QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText("\n".join(users), mode=cb.Clipboard)

	def doIRCUrlCopy(self):

		url = f"irc://{self.parent.server}/{self.name}"

		cb = QApplication.clipboard()
		cb.clear(mode=cb.Clipboard )
		cb.setText(f"{url}", mode=cb.Clipboard)

	def saveAsTextDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Chat As...",INSTALL_DIRECTORY,"Text Files (*.txt);;All Files (*)", options=options)
		if fileName:
			self.FILENAME = fileName
			if '.' in fileName:
				pass
			else:
				fileName = fileName + '.txt'
			chatlog = open(fileName,"w")
			l = "\n".join(self.parent.windows[self.name].chat)
			chatlog.write(l)

	def saveAsHtmlDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Chat As...",INSTALL_DIRECTORY,"HTML Files (*.html);;All Files (*)", options=options)
		if fileName:
			self.FILENAME = fileName
			if '.' in fileName:
				pass
			else:
				fileName = fileName + '.html'
			chatlog = open(fileName,"w")
			chatlog.write(self.channelChatDisplay.toHtml())


	def buildInterface(self):
		self.setWindowTitle(" "+self.name)


		if not self.isserver:
			menubar = self.menuBar()

			if self.is_channel:

				actMenu = menubar.addMenu("Channel")

				self.actText = QAction(QIcon(FILE_ICON),"Save chat as text",self)
				self.actText.triggered.connect(self.saveAsTextDialog)
				actMenu.addAction(self.actText)

				self.actHtml = QAction(QIcon(HTML_ICON),"Save chat as HTML",self)
				self.actHtml.triggered.connect(self.saveAsHtmlDialog)
				actMenu.addAction(self.actHtml)

				clipMenu = actMenu.addMenu(QIcon(CLIPBOARD_ICON),"Copy to clipboard")

				self.actSaveUrl = QAction("IRC server/channel URL",self)
				self.actSaveUrl.triggered.connect(self.doIRCUrlCopy)
				clipMenu.addAction(self.actSaveUrl)

				self.actSaveTopic = QAction("Channel topic",self)
				self.actSaveTopic.triggered.connect(self.doTopicCopy)
				clipMenu.addAction(self.actSaveTopic)

				self.actSaveUsers = QAction("Channel users",self)
				self.actSaveUsers.triggered.connect(self.doUserCopy)
				clipMenu.addAction(self.actSaveUsers)

				actMenu.addSeparator()

				self.actPart = QAction(QIcon(EXIT_ICON),"Leave channel",self)
				self.actPart.triggered.connect(self.doPart)
				actMenu.addAction(self.actPart)

			else:

				# User window
				actMenu = menubar.addMenu("Private")

				self.actText = QAction(QIcon(FILE_ICON),"Save chat as text",self)
				self.actText.triggered.connect(self.saveAsTextDialog)
				actMenu.addAction(self.actText)

				self.actHtml = QAction(QIcon(HTML_ICON),"Save chat as HTML",self)
				self.actHtml.triggered.connect(self.saveAsHtmlDialog)
				actMenu.addAction(self.actHtml)

				self.actWhois = QAction(QIcon(USER_ICON),"Whois User",self)
				self.actWhois.triggered.connect(self.doUserWhois)
				actMenu.addAction(self.actWhois)

				actMenu.addSeparator()

				self.actPart = QAction(QIcon(EXIT_ICON),"Close Window",self)
				self.actPart.triggered.connect(self.doLeave)
				actMenu.addAction(self.actPart)

		if self.isserver:
			self.setWindowIcon(QIcon(SERVER_ICON))
		else:
			if self.is_channel:
				self.setWindowIcon(QIcon(CHANNEL_ICON))
			else:
				self.setWindowIcon(QIcon(USER_ICON))

		# Main window
		self.channelChatDisplay = QTextBrowser(self)
		self.channelChatDisplay.setObjectName("channelChatDisplay")
		self.channelChatDisplay.setFocusPolicy(Qt.NoFocus)

		self.channelChatDisplay.anchorClicked.connect(self.linkClicked)

		if self.is_channel:
			self.channelUserDisplay = QListWidget(self)
			self.channelUserDisplay.setObjectName("channelUserDisplay")
			self.channelUserDisplay.installEventFilter(self)
			self.channelUserDisplay.setFont(self.fontBold)

		self.userTextInput = QLineEdit(self)
		self.userTextInput.setObjectName("userTextInput")
		self.userTextInput.returnPressed.connect(self.handleUserInput)

		# Layout
		if self.is_channel:
			self.horizontalSplitter = QSplitter(Qt.Horizontal)
			self.horizontalSplitter.addWidget(self.channelChatDisplay)
			self.horizontalSplitter.addWidget(self.channelUserDisplay)
			self.horizontalSplitter.setSizes([400,100])

		self.verticalSplitter = QSplitter(Qt.Vertical)
		if self.is_channel:
			self.verticalSplitter.addWidget(self.horizontalSplitter)
		else:
			self.verticalSplitter.addWidget(self.channelChatDisplay)
		self.verticalSplitter.addWidget(self.userTextInput)
		self.verticalSplitter.setSizes([475,25])

		# Make sure the background and text color is from the colors.json
		# This is loaded into the parent at startup
		self.channelChatDisplay.setStyleSheet(f"background-color: {self.parent.colors[0]}; color: {self.parent.colors[1]};")
		self.userTextInput.setStyleSheet(f"background-color: {self.parent.colors[0]}; color: {self.parent.colors[1]};")
		if self.is_channel: self.channelUserDisplay.setStyleSheet(f"background-color: {self.parent.colors[0]}; color: {self.parent.colors[1]};")

		finalLayout = QVBoxLayout()
		finalLayout.setContentsMargins(0, 0, 0, 0)
		finalLayout.addWidget(self.verticalSplitter)

		x = QWidget()
		x.setLayout(finalLayout)
		self.setCentralWidget(x)

		self.userTextInput.setFocus()

	# Context menus
	def eventFilter(self, source, event):

		# User List Menu
		if (event.type() == QtCore.QEvent.ContextMenu and source is self.channelUserDisplay):

			item = source.itemAt(event.pos())
			if item is None: return True

			user = item.text()
			if '@' in user:
				user_op = True
			else:
				user_op = False
			if '+' in user:
				user_voiced = True
			else:
				user_voiced = False
			user = user.replace("@","")
			user = user.replace("+","")
			user = user.replace("%","")
			user = user.replace("~","")
			user = user.replace("&","")

			if user == self.parent.nickname:
				if not self.is_op:
					if not self.is_voiced:
						return True
				menu = QMenu()
				actDeop = menu.addAction('De-op self')
				actDevoice = menu.addAction('De-voice self')
				if self.is_op:
					actDevoice.setVisible(False)
				if self.is_voiced:
					actDeop.setVisible(False)
				action = menu.exec_(self.channelUserDisplay.mapToGlobal(event.pos()))
				if action == actDeop:
					#self.parent.irc.connection.send_items('MODE', self.channel, "-o", self.parent.nickname)
					self.irc.mode(self.name,False,"o",None,self.parent.nickname)
					return True
				if action == actDevoice:
					#self.parent.irc.connection.send_items('MODE', self.channel, "-v", self.parent.nickname)
					self.irc.mode(self.name,False,"v",None,self.parent.nickname)
					return True
				return True

			menu = QMenu()

			if self.is_op:
				infoChan = menu.addAction(f"{self.parent.nickname} (Operator)")
			elif self.is_voiced:
				infoChan = menu.addAction(f"{self.parent.nickname} (Voiced)")
			else:
				infoChan = menu.addAction(f"{self.parent.nickname}")

			infoChan.setFont(self.fontBoldItalic)
			menu.addSeparator()

			actWhois = menu.addAction('Whois User')
			actNotice = menu.addAction('Notice User')
			actMsg = menu.addAction('Message User')
			actWinMsg = menu.addAction('New Chat Window')

			if self.is_op: menu.addSeparator()

			actOp = menu.addAction('Give ops')
			actDeop = menu.addAction('Take ops')

			actVoice = menu.addAction('Give voice')
			actDevoice = menu.addAction('Take voice')

			if user_op:
				actOp.setVisible(False)
			else:
				actDeop.setVisible(False)

			if user_voiced:
				actVoice.setVisible(False)
			else:
				actDevoice.setVisible(False)

			actKick = menu.addAction('Kick')
			actBan = menu.addAction('Ban')

			if len(self.banned)>0:
				if self.is_op:
					menuBanned = menu.addMenu("Remove Ban")
					for u in self.banned:
						action = menuBanned.addAction(f"{u}")
						action.triggered.connect(
							lambda state,user=u: self.unban(user))

			if not self.is_op:
				actOp.setVisible(False)
				actDeop.setVisible(False)
				actVoice.setVisible(False)
				actDevoice.setVisible(False)
				actKick.setVisible(False)
				actBan.setVisible(False)

			action = menu.exec_(self.channelUserDisplay.mapToGlobal(event.pos()))

			if action == actWhois:
				self.irc.whois(user)
				return True

			if action == actMsg:
				self.userTextInput.setText(f"/msg {user} ")
				self.userTextInput.setFocus()
				return True

			if action == actWinMsg:
				if user in self.parent.windows:
					self.parent.windows[user].window.userTextInput.setFocus()
				else:
					self.parent.newChatWindow(user)
					self.parent.windows[user].window.userTextInput.setFocus()
				return True

			if action == actNotice:
				self.userTextInput.setText(f"/notice {user} ")
				self.userTextInput.setFocus()
				return True

			if action == actOp:
				#self.parent.irc.connection.send_items('MODE', self.channel, "+o", user)
				self.irc.mode(self.name,True,"o",None,user)
				return True

			if action == actDeop:
				#self.parent.irc.connection.send_items('MODE', self.channel, "-o", user)
				self.irc.mode(self.name,False,"o",None,user)
				return True

			if action == actVoice:
				#self.parent.irc.connection.send_items('MODE', self.channel, "+v", user)
				self.irc.mode(self.name,True,"v",None,user)
				return True

			if action == actDevoice:
				#self.parent.irc.connection.send_items('MODE', self.channel, "-v", user)
				self.irc.mode(self.name,False,"v",None,user)
				return True

			if action == actKick:
				#self.parent.irc.connection.send_items('KICK', self.channel, user)
				self.irc.kick(self.name,user)
				return True

			if action == actBan:
				uh = self.getUserHostmask(user)
				if uh == None:
					#self.parent.irc.connection.send_items('MODE', self.channel, "+b", user)
					self.irc.mode(self.name,True,"b",None,user)
					self.banned.append(user)
				else:
					#self.parent.irc.connection.send_items('MODE', self.channel, "+b", f"*@{uh}")
					self.irc.mode(self.name,True,"b",None,user,f"*@{uh}")
					self.banned.append(f"*@{uh}")
				return True

		return super(Viewer, self).eventFilter(source, event)

	def unban(self,user):
		#self.parent.irc.connection.send_items('MODE', self.channel, "-b", user)
		self.irc.mode(self.name,False,"b",None,user)
		bc = []
		for u in self.banned:
			if u == user: continue
			bc.append(u)
		self.banned = bc

	def getUserHostmask(self,nick):
		for u in self.userlist:
			if '!' in u:
				up = u.split('!')
				if nick == up[0]:
					m = up[1].split('@')
					return m[1]
		return None

	def setUserList(self,ulist):
		self.channelUserDisplay.clear()
		self.userlist = []
		self.users = []
		for n in ulist:
			p = n.split('!')


			# Strip channel status symbols for storage
			ue = n
			if ue[0]=='@': ue = ue.replace('@','',1)
			if ue[0]=='+': ue = ue.replace('+','',1)
			if ue[0]=='~': ue = ue.replace('~','',1)
			if ue[0]=='&': ue = ue.replace('&','',1)
			if ue[0]=='%': ue = ue.replace('%','',1)
			self.userlist.append(ue)

			# Check for client channel status
			if p[0] == self.parent.nickname:
				self.is_op = False
				self.is_voiced = False
			if p[0] == f"@{self.parent.nickname}": self.is_op = True
			if p[0] == f"+{self.parent.nickname}": self.is_voiced = True
			
			# Add nick to the user display
			self.channelUserDisplay.addItem(p[0])

			# Store user list
			self.users.append(p[0])

	def cleanUserList(self,ulist):
		self.channelUserDisplay.clear()

	def addUser(self,data):
		self.channelUserDisplay.addItem(data)

	def hasUser( self, text ):
		for u in [str(self.channelUserDisplay.item(i).text()) for i in range(self.channelUserDisplay.count())]:
			u = u.replace('@','')
			u = u.replace('+','')
			u = u.replace('~','')
			u = u.replace('&','')
			u = u.replace('%','')
			if u == text: return True
		return False


	def removeUser( self, text ):
		items = self.channelUserDisplay.findItems(text,Qt.MatchExactly)
		if len(items) > 0:
			for item in items:
				self.channelUserDisplay.takeItem(self.channelUserDisplay.row(item))

	def writeText(self,text):
		self.channelChatDisplay.append(text)
		self.channelChatDisplay.moveCursor(QTextCursor.End)

		#self.log.append(remove_html_markup(text))

	def keyPressEvent(self,event):
		if len(self.history_buffer)==0: return
		if event.key() == Qt.Key_Up:
			self.history_buffer_pointer = self.history_buffer_pointer + 1
			if self.history_buffer_pointer > self.history_buffer_max: self.history_buffer_pointer = self.history_buffer_max
			if self.history_buffer_pointer > (len(self.history_buffer)-1): self.history_buffer_pointer = len(self.history_buffer) - 1
			self.userTextInput.setText(self.history_buffer[self.history_buffer_pointer])
		if event.key() == Qt.Key_Down:
			self.history_buffer_pointer = self.history_buffer_pointer - 1
			if self.history_buffer_pointer <= 0: self.history_buffer_pointer = 0
			self.userTextInput.setText(self.history_buffer[self.history_buffer_pointer])

	# Handle user input
	def handleUserInput(self):
		user_input = self.userTextInput.text()
		self.userTextInput.setText('')

		self.history_buffer.insert(0,user_input)
		if len(self.history_buffer)>self.history_buffer_max:
			self.history_buffer.pop()
		self.history_buffer_pointer = 0

		if self.is_channel:
			# self.parent.handleChannelInput(self.name,user_input)
			if self.parent.handleChannelInput(self.name,user_input):
				return
		else:
			if self.parent.handleUserInput(self.name,user_input):
				return

		tokens = user_input.split(' ')

		if len(tokens)>0:

			# /join
			if tokens[0].lower() == "/join":
				if len(tokens)>=3:
					tokens.pop(0)
					channel = tokens.pop(0)
					key = " ".join(tokens)
					self.parent.irc.join(channel,key)
				elif len(tokens)==2:
					tokens.pop(0)
					channel = tokens.pop(0)
					self.parent.irc.join(channel)
				else:
					d = system_display("Usage: /join CHANNEL [KEY]")
					self.parent.windows[self.name].window.writeText(d)
					return

			# /nick
			if tokens[0].lower() == "/nick":
				if len(tokens)==2:
					newnick = tokens[1]
					self.parent.irc.setNick(newnick)
					return
				else:
					d = system_display("Usage: /nick NEW_NICK")
					self.parent.windows[self.name].window.writeText(d)
					return

			# /me
			if self.is_channel:
				if tokens[0].lower() == "/me":
					if len(tokens)>=2:
						tokens.pop(0)
						msg = ' '.join(tokens)
						self.parent.irc.describe(self.name,msg)
						d = action_display(self.parent.nickname,msg)
						self.parent.windows[self.name].window.writeText(d)
						self.parent.windows[self.name].chat.append(f"{self.parent.getTimestamp()} ACTION {self.name} {self.parent.nickname} {msg}")
						return
					else:
						d = system_display("Usage: /me MESSAGE")
						self.parent.windows[self.name].window.writeText(d)
						return

			# /whois
			if tokens[0].lower() == "/whois":
				if len(tokens)==2:
					target = tokens[1]
					self.parent.irc.whois(target)
					return
				else:
					d = system_display("Usage: /whois TARGET")
					self.parent.windows[self.name].window.writeText(d)
					return

			# /msg
			if tokens[0].lower() == "/msg":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					if self.irc:
						self.irc.msg(target,msg,MAXIMUM_IRC_MESSAGE_SIZE)
					else:
						self.parent.irc.msg(target,msg,MAXIMUM_IRC_MESSAGE_SIZE)
					if target in self.parent.windows:
						#self.windows[target].window.writeText(f"{nick}: {msg}")
						d = mychat_display(self.parent.nickname,msg,MAX_USERNAME_SIZE)
						self.parent.windows[target].window.writeText(d)
						self.parent.windows[target].chat.append(f"{self.parent.getTimestamp()} {target} {self.parent.nickname}: {msg}")
					else:
						if len(target)>0:
							if target[0]!='#':
								# its a user, open a window
								self.parent.newChatWindow(target)
								d = mychat_display(self.parent.nickname,msg,MAX_USERNAME_SIZE)
								self.parent.windows[target].window.writeText(d)
								self.parent.windows[target].chat.append(f"{self.parent.getTimestamp()} PRIVATE {target} {self.parent.nickname}: {msg}")
					return
				else:
					d = system_display("Usage: /msg TARGET MESSAGE")
					self.parent.windows[self.name].window.writeText(d)
					return

			# /notice
			if tokens[0].lower() == "/notice":
				if len(tokens)>=3:
					tokens.pop(0)
					target = tokens.pop(0)
					msg = ' '.join(tokens)
					if self.irc:
						self.irc.notice(target,msg)
						self.parent.windows[target].chat.append(f"{self.parent.getTimestamp()} NOTICE {target} {self.parent.nickname}: {msg}")
					else:
						self.parent.irc.notice(target,msg)
					if target in self.parent.windows:
						#self.windows[target].window.writeText(f"{nick}: {msg}")
						d = notice_display(self.parent.nickname,msg,MAX_USERNAME_SIZE)
						self.parent.windows[target].window.writeText(d)
						self.parent.windows[target].chat.append(f"{self.parent.getTimestamp()} NOTICE {target} {self.parent.nickname}: {msg}")
					return
				else:
					d = system_display("Usage: /notice TARGET MESSAGE")
					self.parent.windows[self.name].window.writeText(d)
					return


		#self.parent.windows[self.name].window.writeText(f"{self.parent.nickname}: {user_input}")

		if self.isserver: return
		
		if self.is_channel:
			self.irc.msg(f"{self.name}",f"{user_input}",MAXIMUM_IRC_MESSAGE_SIZE)
		else:
			p = self.name.split('!')
			if len(p)==2:
				self.irc.msg(f"{p[0]}",f"{user_input}",MAXIMUM_IRC_MESSAGE_SIZE)
			else:
				self.irc.msg(f"{self.name}",f"{user_input}",MAXIMUM_IRC_MESSAGE_SIZE)

		d = mychat_display(self.parent.nickname,user_input,MAX_USERNAME_SIZE)
		self.parent.windows[self.name].window.writeText(d)
		self.parent.windows[self.name].chat.append(f"{self.parent.getTimestamp()} {self.name} {self.parent.nickname}: {user_input}")

	# Handle user input
	def setTopic(self,topic):
		self.setWindowTitle(" "+f"{self.name} - {topic}")
		self.topic = topic

	def clearTopic(self):
		self.setWindowTitle(" "+self.name)

	# def setTopic(self,topic):
	# 	self.channelTopic.setText(topic)
	# 	if not topic.isspace():
	# 		self.topic = topic

	# If users click on URLs, they will open in the default browser
	def linkClicked(self,url):
		link = url.toString()
		if url.host():
			QDesktopServices.openUrl(url)
			self.channelChatDisplay.setSource(QUrl())

	# Exit the program if the window is closed
	def closeEvent(self, event):
		#self.app.quit()
		pass
