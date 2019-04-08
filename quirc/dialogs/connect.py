
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
		# self.user_data['nickname'] = str(self.nick.text())
		# self.user_data['username'] = str(self.username.text())
		# self.user_data['realname'] = str(self.realname.text())
		if self.DIALOG_CONNECT_VIA_SSL:
			use_ssl = 1
		else:
			use_ssl = 0
		#save_user_information(self.user_data)
		# Only save server if it host isn't empty, and port is an integer
		# if is_integer(self.port.text()):
		# 	if len(self.host.text())>0:
		# 		save_last_server( str(self.host.text()), int( self.port.text() ), str(self.password.text()), self.DIALOG_CONNECT_VIA_SSL )
		# # Save user information
		# user = {
		# 	"nick": str(self.nick.text()),
		# 	"username": str(self.username.text()),
		# 	"realname": str(self.realname.text())
		# }
		# save_user(user)
		retval = map(str, [self.nick.text(), self.username.text(), self.realname.text(), self.host.text(), self.port.text(), self.password.text()])
		retval = list(retval)
		retval.append(str(use_ssl))
		return retval

	def clickSSL(self,state):
		if state == Qt.Checked:
			self.DIALOG_CONNECT_VIA_SSL = True
		else:
			self.DIALOG_CONNECT_VIA_SSL = False

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.DIALOG_CONNECT_VIA_SSL = False

		self.setWindowTitle(f"Connect to IRC")
		self.setWindowIcon(QIcon(SERVER_ICON))

		last_server = get_last_server()
		user = get_user()

		# Server information
		hostLayout = QHBoxLayout()
		self.hostLabel = QLabel("Server")
		#self.host = QLineEdit("localhost")
		self.host = QLineEdit(last_server["host"])
		hostLayout.addWidget(self.hostLabel)
		hostLayout.addStretch()
		hostLayout.addWidget(self.host)

		portLayout = QHBoxLayout()
		self.portLabel = QLabel("Port")
		#self.port = QLineEdit(str(6667))
		self.port = QLineEdit(str(last_server["port"]))
		portLayout.addWidget(self.portLabel)
		portLayout.addStretch()
		portLayout.addWidget(self.port)

		passLayout = QHBoxLayout()
		self.passLabel = QLabel("Password")
		#self.password = QLineEdit()
		self.password = QLineEdit(last_server["password"])
		passLayout.addWidget(self.passLabel)
		passLayout.addStretch()
		passLayout.addWidget(self.password)

		self.ssl = QCheckBox("Connect via SSL",self)
		self.ssl.stateChanged.connect(self.clickSSL)

		if last_server["ssl"]:
			self.ssl.toggle()


		# if int(self.server_data['ssl']) == 1:
		# 	self.ssl.toggle()

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
		#self.nick = QLineEdit(DEFAULT_NICKNAME)
		self.nick = QLineEdit(user["nick"])
		nickLayout.addWidget(self.nickLabel)
		nickLayout.addStretch()
		nickLayout.addWidget(self.nick)

		userLayout = QHBoxLayout()
		self.userLabel = QLabel("Username")
		#self.username = QLineEdit(DEFAULT_USERNAME)
		self.username = QLineEdit(user["username"])
		userLayout.addWidget(self.userLabel)
		userLayout.addStretch()
		userLayout.addWidget(self.username)

		realLayout = QHBoxLayout()
		self.realLabel = QLabel("Real Name")
		#self.realname = QLineEdit(DEFAULT_IRCNAME)
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