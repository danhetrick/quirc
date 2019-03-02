
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
	def get_limit_information(client,parent=None):
		dialog = Dialog(parent)
		dialog.msg.setFont(parent.parent.bold_userlist_font)
		dialog.msg2.setFont(parent.parent.userlist_font)
		r = dialog.exec_()
		if r:
			return dialog.return_integer(client,parent)
		return None

	def return_integer(self,client,parent):
		x = int(self.sp.value())
		client.send_items('MODE', parent.channel, "+l", str(x))
		return x

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.setWindowTitle(f"Channel Limit")

		self.msg = QLabel("Set user limit")
		self.msg.setAlignment(Qt.AlignCenter)

		self.msg2 = QLabel("0 = no limit")
		self.msg2.setAlignment(Qt.AlignCenter)

		self.sp = QSpinBox()
		self.sp.setValue(parent.info[CHANNEL_INFO_LIMIT])

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(self.msg)
		finalLayout.addWidget(self.msg2)
		finalLayout.addStretch()
		finalLayout.addWidget(self.sp)
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)