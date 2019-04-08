
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from quirc.common import *

class Dialog(QDialog):

	@staticmethod
	def get_nick_information(parent=None):
		dialog = Dialog(parent)
		r = dialog.exec_()
		if r:
			return dialog.return_string()
		return None

	def return_string(self):
		retval = str(self.name.text())
		return retval

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.setWindowTitle(f"New Nickname")
		self.setWindowIcon(QIcon(USER_ICON))

		nameLayout = QHBoxLayout()
		self.nameLabel = QLabel("Nickname")
		self.name = QLineEdit()
		nameLayout.addWidget(self.nameLabel)
		nameLayout.addWidget(self.name)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.accept)
		buttons.rejected.connect(self.reject)

		finalLayout = QVBoxLayout()
		finalLayout.addLayout(nameLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
