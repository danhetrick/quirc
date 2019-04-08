
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from quirc.common import *

class Dialog(QDialog):

	@staticmethod
	def get_channel_information(parent=None):
		dialog = Dialog(parent)
		r = dialog.exec_()
		if r:
			return dialog.return_strings()
		return None

	def return_strings(self):
		retval = map(str, [self.name.text(), self.key.text()])
		retval = list(retval)
		return retval

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.setWindowTitle(f"Join Channel")
		self.setWindowIcon(QIcon(CHANNEL_ICON))

		nameLayout = QHBoxLayout()
		self.nameLabel = QLabel("Channel")
		self.name = QLineEdit()
		nameLayout.addWidget(self.nameLabel)
		nameLayout.addStretch()
		nameLayout.addWidget(self.name)

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
		finalLayout.addLayout(nameLayout)
		finalLayout.addLayout(keyLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
