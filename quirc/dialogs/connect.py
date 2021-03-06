
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

import quirc.dialogs.add_channel as AddChannelDialog

class Dialog(QDialog):

	@staticmethod
	def get_connect_information(can_do_ssl,parent=None):
		dialog = Dialog(can_do_ssl,parent)
		r = dialog.exec_()
		if r:
			return dialog.return_strings()
		return None

	def return_strings(self):

		items = [] 
		for index in range(self.autoChannels.count()): 
			 items.append(self.autoChannels.item(index).text())

		save_autojoin_channels(items)

		if self.DIALOG_CONNECT_VIA_SSL:
			use_ssl = 1
		else:
			use_ssl = 0
		retval = map(str, [self.nick.text(), self.username.text(), self.realname.text(), self.host.text(), self.port.text(), self.password.text()])
		retval = list(retval)
		retval.append(str(use_ssl))
		return retval

	def clickSSL(self,state):
		if state == Qt.Checked:
			self.DIALOG_CONNECT_VIA_SSL = True
		else:
			self.DIALOG_CONNECT_VIA_SSL = False

	def doAddChannel(self):
		self.x = AddChannelDialog.Dialog(self)
		self.x.show()

	def doRemoveChannel(self):
		self.removeSel()

	def removeSel(self):
	    listItems=self.autoChannels.selectedItems()
	    if not listItems: return        
	    for item in listItems:
	       self.autoChannels.takeItem(self.autoChannels.row(item))

	def __init__(self,can_do_ssl,parent=None):
		super(Dialog,self).__init__(parent)

		self.can_do_ssl = can_do_ssl
		self.parent = parent

		self.DIALOG_CONNECT_VIA_SSL = False

		self.setWindowTitle(f"Connect to IRC")
		self.setWindowIcon(QIcon(SERVER_ICON))

		last_server = get_last_server()
		user = get_user()
		aj = get_autojoins()

		# Server information
		hostLayout = QHBoxLayout()
		self.hostLabel = QLabel("Server")
		self.host = QLineEdit(last_server["host"])
		hostLayout.addWidget(self.hostLabel)
		hostLayout.addStretch()
		hostLayout.addWidget(self.host)

		portLayout = QHBoxLayout()
		self.portLabel = QLabel("Port")
		self.port = QLineEdit(str(last_server["port"]))
		portLayout.addWidget(self.portLabel)
		portLayout.addStretch()
		portLayout.addWidget(self.port)

		passLayout = QHBoxLayout()
		self.passLabel = QLabel("Password")
		self.password = QLineEdit(last_server["password"])
		passLayout.addWidget(self.passLabel)
		passLayout.addStretch()
		passLayout.addWidget(self.password)

		self.ssl = QCheckBox("Connect via SSL",self)
		self.ssl.stateChanged.connect(self.clickSSL)

		if last_server["ssl"]:
			self.ssl.toggle()

		if not self.can_do_ssl:
			self.DIALOG_CONNECT_VIA_SSL = False
			self.ssl.setEnabled(False)

		servLayout = QVBoxLayout()
		servLayout.addLayout(hostLayout)
		servLayout.addLayout(portLayout)
		servLayout.addLayout(passLayout)
		servLayout.addWidget(self.ssl)

		servBox = QGroupBox("IRC Server")
		servBox.setLayout(servLayout)

		# User information
		nickLayout = QHBoxLayout()
		self.nickLabel = QLabel("Nick")
		self.nick = QLineEdit(user["nick"])
		nickLayout.addWidget(self.nickLabel)
		nickLayout.addStretch()
		nickLayout.addWidget(self.nick)

		userLayout = QHBoxLayout()
		self.userLabel = QLabel("Username")
		self.username = QLineEdit(user["username"])
		userLayout.addWidget(self.userLabel)
		userLayout.addStretch()
		userLayout.addWidget(self.username)

		realLayout = QHBoxLayout()
		self.realLabel = QLabel("Real Name")
		self.realname = QLineEdit(user["realname"])
		realLayout.addWidget(self.realLabel)
		realLayout.addStretch()
		realLayout.addWidget(self.realname)

		nurLayout = QVBoxLayout()
		nurLayout.addLayout(nickLayout)
		nurLayout.addLayout(userLayout)
		nurLayout.addLayout(realLayout)

		nickBox = QGroupBox("User Information")
		nickBox.setLayout(nurLayout)

		#############################
		# autojoin channels

		self.autoChannels = QListWidget(self)
		self.autoChannels.setMaximumWidth(175)
		#self.parent.autoChannels.addItem(f"{channel}")
		for c in aj:
			p = c.split('/')
			if len(p)==2:
				# x = self.autoChannels.addItem(c)
				# x.setIcon(QIcon(LOCKED_ICON))
				item = QListWidgetItem(c)
				item.setIcon(QIcon(LOCKED_ICON))
				self.autoChannels.addItem(item)
			else:
				# x = self.autoChannels.addItem(c)
				# x.setIcon(QIcon(CHANNEL_ICON))
				item = QListWidgetItem(c)
				item.setIcon(QIcon(CHANNEL_ICON))
				self.autoChannels.addItem(item)

		self.addChannelButton = QPushButton("+")
		self.addChannelButton.clicked.connect(self.doAddChannel)

		self.removeChannelButton = QPushButton("-")
		self.removeChannelButton.clicked.connect(self.doRemoveChannel)

		buttonLayout = QHBoxLayout()
		buttonLayout.addStretch()
		buttonLayout.addWidget(self.addChannelButton)
		buttonLayout.addWidget(self.removeChannelButton)

		autoJoinLayout = QVBoxLayout()
		autoJoinLayout.addWidget(self.autoChannels)
		autoJoinLayout.addLayout(buttonLayout)
		

		chanBox = QGroupBox("Auto-Join Channels")
		chanBox.setLayout(autoJoinLayout)

		#############################

		vLayout = QVBoxLayout()
		vLayout.addWidget(nickBox)
		vLayout.addWidget(servBox)

		tLayout = QHBoxLayout()
		tLayout.addLayout(vLayout)
		tLayout.addWidget(chanBox)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		finalLayout = QVBoxLayout()
		#finalLayout.addWidget(nickBox)
		#finalLayout.addWidget(servBox)
		finalLayout.addLayout(tLayout)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
