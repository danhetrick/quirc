import sys
import json

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from Quirc.Settings import *

class Dialog(QDialog):

	def connect(self):
		if self.USE_CUSTOM:
			host = self.host.text()
			port = self.port.text()

			if host == "":
				QMessageBox.about(self, "Error", "No host entered!")
				return

			if port == "":
				QMessageBox.about(self, "Error", "No port entered!")
				return

			global SERVER_PASSWORD

			p = self.password.text()
			if p != '':
				SERVER_PASSWORD = p

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

			if self.DIALOG_CONNECT_VIA_SSL:
				self.PARENT.setNetworkInformation(host,port)
				self.PARENT.SSL_Connect(host,port)
			else:
				self.PARENT.setNetworkInformation(host,port)
				self.PARENT.TCP_Connect(host,port)

			self.close()
		else:

			h = self.StoredData[self.StoredServer]

			host = h[0]
			port = int(h[1])

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

			self.PARENT.setNetworkInformation(host,port)
			if "ssl" in h[3]:
				self.PARENT.SSL_Connect(host,port)
			else:
				self.PARENT.TCP_Connect(host,port)

			self.close()

	def setServer(self):
		self.StoredServer = self.servers.currentIndex()

		self.netType.setText("<b>"+self.StoredData[self.StoredServer][2]+" IRC Network</b>")
		if "ssl" in self.StoredData[self.StoredServer][3]:
			self.connType.setText(f"<i>Connect via SSL to port {self.StoredData[self.StoredServer][1]}</i>")
		else:
			self.connType.setText(f"<i>Connect via TCP/IP to port {self.StoredData[self.StoredServer][1]}</i>")

	def clickSSL(self,state):
		if state == Qt.Checked:
			self.DIALOG_CONNECT_VIA_SSL = True
		else:
			self.DIALOG_CONNECT_VIA_SSL = False
	
	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)
		self.PARENT = parent
		self.DIALOG_CONNECT_VIA_SSL = False
		self.StoredServer = 0
		self.USE_CUSTOM = False
		self.StoredData = []

		self.setWindowTitle(f"Connect")
		self.setWindowIcon(QIcon(CONNECT_ICON))

		hostLayout = QHBoxLayout()
		self.hostLabel = QLabel("Server")
		self.host = QLineEdit()
		hostLayout.addWidget(self.hostLabel)
		hostLayout.addStretch()
		hostLayout.addWidget(self.host)

		portLayout = QHBoxLayout()
		self.portLabel = QLabel("Port")
		self.port = QLineEdit()
		portLayout.addWidget(self.portLabel)
		portLayout.addStretch()
		portLayout.addWidget(self.port)

		passLayout = QHBoxLayout()
		self.passLabel = QLabel("Password")
		self.password = QLineEdit()
		passLayout.addWidget(self.passLabel)
		passLayout.addStretch()
		passLayout.addWidget(self.password)

		self.ssl = QCheckBox("Connect via SSL",self)
		self.ssl.stateChanged.connect(self.clickSSL)

		self.go = QPushButton("Connect")
		self.go.clicked.connect(self.connect)

		self.canc = QPushButton("Cancel")
		self.canc.clicked.connect(self.close)

		servLayout = QVBoxLayout()
		servLayout.addLayout(hostLayout)
		servLayout.addLayout(portLayout)
		servLayout.addLayout(passLayout)
		servLayout.addWidget(self.ssl)

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

		nurLayout = QVBoxLayout()
		nurLayout.addLayout(nickLayout)
		nurLayout.addLayout(userLayout)
		nurLayout.addLayout(realLayout)

		nickBox = QGroupBox("User Information")
		nickBox.setLayout(nurLayout)

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

		script = open(STORED_SERVER_FILE,"r")
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
			self.connType.setText(f"<i>Connect via SSL to port {self.StoredData[self.StoredServer][1]}</i>")
		else:
			self.connType.setText(f"<i>Connect via TCP/IP to port {self.StoredData[self.StoredServer][1]}</i>")

		sdLayout = QHBoxLayout()
		sd = QLabel("Select an IRC server below")
		sdLayout.addStretch()
		sdLayout.addWidget(sd)
		sdLayout.addStretch()

		fstoreLayout = QVBoxLayout()
		fstoreLayout.addLayout(sdLayout)
		fstoreLayout.addWidget(self.servers)
		fstoreLayout.addStretch()
		fstoreLayout.addLayout(ntLayout)
		fstoreLayout.addLayout(ctLayout)
		fstoreLayout.addStretch()

		tabs = QTabWidget()
		tabCustom = QWidget()
		tabStored = QWidget()

		tabs.tabBarClicked.connect(self.tabClick)

		tabCustom.setLayout(servLayout)
		tabStored.setLayout(fstoreLayout)

		tabs.addTab(tabStored,"Public Server")
		tabs.addTab(tabCustom,"Custom Server")

		layout = QHBoxLayout()

		layout.setSizeConstraint(QLayout.SetFixedSize)

		layout.addWidget(nickBox)
		layout.addWidget(tabs)

		buttonsLayout = QHBoxLayout()
		buttonsLayout.addWidget(self.go)
		buttonsLayout.addWidget(self.canc)

		finalLayout = QVBoxLayout()
		finalLayout.addLayout(layout)
		finalLayout.addLayout(buttonsLayout)

		self.setLayout(finalLayout)

		#layout.addLayout(buttonsLayout)

		# layout.addWidget(self.go)
		# layout.addWidget(self.canc)

		# self.setLayout(layout)

		self.setFixedSize(self.sizeHint())

	def tabClick(self,index):
		if index == 0:
			self.USE_CUSTOM = False
		else:
			self.USE_CUSTOM = True

