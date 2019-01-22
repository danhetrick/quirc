import sys
import time

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from Quirc.Settings import *

cGUI = None
pGUI = None
pHOST = ''
MAX_TIMEOUT_TIME = 10

class Timeout(QRunnable):

	def run(self):
		global pGUI
		global cGUI
		global pHOST
		count = 0
		while count < MAX_TIMEOUT_TIME:
			if cGUI.WORKING:
				time.sleep(1)
			else:
				pass
			count += 1
		pGUI(pHOST)

class Dialog(QDialog):

	def connected(self):
		self.close()

	def __init__(self,host,parent=None):
		super(Dialog,self).__init__(parent)
		self.WORKING = True

		self.setModal(True)

		self.setWindowTitle(f"Connecting")
		self.setWindowIcon(QIcon(QUIRC_ICON))

		self.msgLabel = QLabel(f"<h1>Connecting to {host}</h1>")

		msgLayout = QHBoxLayout()
		msgLayout.addStretch()
		msgLayout.addWidget(self.msgLabel)
		msgLayout.addStretch()

		self.canc = QPushButton("Cancel")
		self.canc.clicked.connect(self.close)

		winLayout = QVBoxLayout()
		winLayout.addLayout(msgLayout)
		winLayout.addWidget(self.canc)

		self.setLayout(winLayout)
		self.setFixedSize(self.sizeHint())

		self.setWindowFlags(
			QtCore.Qt.Tool |
			QtCore.Qt.SplashScreen
			)

		self.show()

