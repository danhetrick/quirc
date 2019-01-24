import sys
import json

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from Quirc.Settings import *

class Dialog(QDialog):

	def save(self):
		uinfo = {
				"nickname": self.nick.text(),
				"username": self.username.text(),
				"realname": self.realname.text()
		}

		if uinfo["nickname"] == "":
			QMessageBox.about(self, "Error", "No nickname entered!")
			return

		if uinfo["username"] == "":
			QMessageBox.about(self, "Error", "No username entered!")
			return

		if uinfo["realname"] == "":
			QMessageBox.about(self, "Error", "No realname entered!")
			return

		with open(USER_INFORMATION_FILE, "w") as write_data:
			json.dump(uinfo, write_data)

		self.close()

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.setWindowTitle(f"User Settings")
		self.setWindowIcon(QIcon(USER_ICON))

		# Load user settings
		with open(USER_INFORMATION_FILE, "r") as read_user:
			data = json.load(read_user)

		nickLayout = QHBoxLayout()
		self.nickLabel = QLabel("Nick")
		self.nick = QLineEdit(data["nickname"])
		nickLayout.addWidget(self.nickLabel)
		nickLayout.addStretch()
		nickLayout.addWidget(self.nick)

		userLayout = QHBoxLayout()
		self.userLabel = QLabel("Username")
		self.username = QLineEdit(data["username"])
		userLayout.addWidget(self.userLabel)
		userLayout.addStretch()
		userLayout.addWidget(self.username)

		realLayout = QHBoxLayout()
		self.realLabel = QLabel("Real Name")
		self.realname = QLineEdit(data["realname"])
		realLayout.addWidget(self.realLabel)
		realLayout.addStretch()
		realLayout.addWidget(self.realname)

		self.go = QPushButton("Save")
		self.go.clicked.connect(self.save)

		self.canc = QPushButton("Cancel")
		self.canc.clicked.connect(self.close)

		nurLayout = QVBoxLayout()
		nurLayout.addLayout(nickLayout)
		nurLayout.addLayout(userLayout)
		nurLayout.addLayout(realLayout)
		nurLayout.addWidget(self.go)
		nurLayout.addWidget(self.canc)

		self.setLayout(nurLayout)

		self.setFixedSize(self.sizeHint())

		