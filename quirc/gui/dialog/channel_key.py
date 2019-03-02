
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
	def get_key_information(msg,parent=None):
		dialog = Dialog(parent)
		dialog.msg.setText(msg)
		dialog.msg.setFont(parent.parent.bold_userlist_font)
		if "Remove" in msg:
			dialog.key.setText(parent.info[CHANNEL_INFO_KEY])
		r = dialog.exec_()
		if r:
			return dialog.return_strings()
		return None

	def return_strings(self):
		return str(self.key.text())

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.setWindowTitle(f"Channel Key")

		self.msg = QLabel("TEXT")
		self.msg.setAlignment(Qt.AlignCenter)

		keyLayout = QHBoxLayout()
		self.keyLabel = QLabel("Key")
		self.key = QLineEdit()
		self.key.setEchoMode(QLineEdit.Password)
		keyLayout.addWidget(self.keyLabel)
		keyLayout.addStretch()
		keyLayout.addWidget(self.key)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(self.msg)
		finalLayout.addStretch()
		finalLayout.addLayout(keyLayout)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)