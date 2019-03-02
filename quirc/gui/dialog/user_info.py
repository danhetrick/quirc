
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

	def saveUser(self):
		nick = self.nick.text()
		user = self.username.text()
		realname = self.realname.text()

		errmsgs = []

		if len(nick)==0:
			errmsgs.append("nickname")

		if len(user)==0:
			errmsgs.append("username")

		if len(realname)==0:
			errmsgs.append("realname")

		if len(errmsgs)>0:
			if len(errmsgs)==3:
				msg = f" No {errmsgs[0]}, {errmsgs[1]}, or {errmsgs[2]} entered!"
			elif len(errmsgs)==2:
				msg = f" No {errmsgs[0]} or {errmsgs[1]} entered!"
			else:
				msg = f" No {errmsgs[0]} entered!"
			self.error_dialog = QErrorMessage()
			self.error_dialog.showMessage(msg)
			self.close()

		uinfo = {
			"nickname": str(nick),
			"username": str(user),
			"realname": str(realname)
		}

		save_user_information(uinfo)
		self.close()

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.user_data = get_user_information()

		self.setWindowTitle(f"User Information")

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

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.saveUser)
		buttons.rejected.connect(self.close)

		finalLayout = QVBoxLayout()
		finalLayout.addLayout(nurLayout)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)