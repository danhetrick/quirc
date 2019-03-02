
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
from quirc.style import *

class Dialog(QDialog):

	@staticmethod
	def get_connect_information(parent=None):
		dialog = Dialog(parent)
		r = dialog.exec_()
		if r:
			return dialog.return_strings()
		return None

	def return_strings(self):
		#   Return list of values. It need map with str (self.lineedit.text() will return QString)
		self.user_data['nickname'] = str(self.nick.text())
		self.user_data['username'] = str(self.username.text())
		self.user_data['realname'] = str(self.realname.text())

		h = self.StoredData[self.StoredServer]
		if "ssl" in h[3]:
			use_ssl = 1
		else:
			use_ssl = 0
		host = h[0]
		port = int(h[1])
		save_user_information(self.user_data)
		# Only save server if it host isn't empty, and port is an integer
		if is_integer(port):
			if len(host)>0:
				save_last_server( host, port, '', str(use_ssl) )
		retval = map(str, [self.nick.text(), self.username.text(), self.realname.text(), host, port, ''])
		retval = list(retval)
		retval.append(str(use_ssl))
		return retval

	def setServer(self):
		self.StoredServer = self.servers.currentIndex()

		self.netType.setText("<b>"+self.StoredData[self.StoredServer][2]+" IRC Network</b>")
		if "ssl" in self.StoredData[self.StoredServer][3]:
			self.connType.setText(f"Connect via SSL to port {self.StoredData[self.StoredServer][1]}")
		else:
			self.connType.setText(f"Connect via TCP/IP to port {self.StoredData[self.StoredServer][1]}")

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.StoredServer = 0
		self.StoredData = []

		self.user_data = get_user_information()

		self.setWindowTitle(f"Connect")
		self.setWindowIcon(QIcon(RESOURCE_ICON_BOOKMARK))

		# Server information
		self.connType = QLabel("")
		self.netType = QLabel("")

		ntLayout = QHBoxLayout()
		ntLayout.addStretch()
		ntLayout.addWidget(self.netType)
		ntLayout.addStretch()

		ctLayout = QHBoxLayout()
		ctLayout.addStretch()
		ctLayout.addWidget(self.connType)
		ctLayout.addStretch()

		self.servers = QComboBox(self)
		self.servers.activated.connect(self.setServer)

		script = open(RESOURCE_SERVER_LIST,"r")
		for line in script:
			x = line.split(":")
			if len(x) != 4: continue
			x[0].strip()
			x[1].strip()
			x[2].strip()
			x[3].strip()
			self.StoredData.append(x)
			self.servers.addItem(x[0])

		self.StoredServer = self.servers.currentIndex()

		self.netType.setText("<b>"+self.StoredData[self.StoredServer][2]+" IRC Network</b>")
		if "ssl" in self.StoredData[self.StoredServer][3]:
			self.connType.setText(f"Connect via SSL to port {self.StoredData[self.StoredServer][1]}")
		else:
			self.connType.setText(f"Connect via TCP/IP to port {self.StoredData[self.StoredServer][1]}")

		fstoreLayout = QVBoxLayout()
		fstoreLayout.addWidget(self.servers)
		fstoreLayout.addStretch()
		fstoreLayout.addLayout(ntLayout)
		fstoreLayout.addLayout(ctLayout)

		servBox = QGroupBox("IRC Network")
		servBox.setLayout(fstoreLayout)
		
		# User information
		nickLayout = QHBoxLayout()
		self.nickLabel = QLabel("Nick")
		self.nick = QLineEdit(self.user_data['nickname'])
		nickLayout.addWidget(self.nickLabel)
		nickLayout.addStretch()
		nickLayout.addWidget(self.nick)

		userLayout = QHBoxLayout()
		self.userLabel = QLabel("Username")
		self.username = QLineEdit(self.user_data['username'])
		userLayout.addWidget(self.userLabel)
		userLayout.addStretch()
		userLayout.addWidget(self.username)

		realLayout = QHBoxLayout()
		self.realLabel = QLabel("Real Name")
		self.realname = QLineEdit(self.user_data['realname'])
		realLayout.addWidget(self.realLabel)
		realLayout.addStretch()
		realLayout.addWidget(self.realname)

		nurLayout = QVBoxLayout()
		nurLayout.addLayout(nickLayout)
		nurLayout.addLayout(userLayout)
		nurLayout.addLayout(realLayout)

		nickBox = QGroupBox("User Information")
		nickBox.setLayout(nurLayout)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(nickBox)
		finalLayout.addWidget(servBox)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)




