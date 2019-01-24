import sys
import json

from PyQt5.QtWidgets import *
app = QApplication(sys.argv)

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from Quirc.Settings import *
from Quirc.Format import *

USER_COLOR_TEXT = "Username Color"
SELF_COLOR_TEXT = "Nickname Color"
ACTION_COLOR_TEXT = "Action Color"
NOTIFY_COLOR_TEXT = "Notification Color"
CHANNEL_COLOR_TEXT = "Channel Info Color"
NOTICE_COLOR_TEXT = "Notice Color"
NORMAL_COLOR_TEXT = "Plain Text Color"
BACKGROUND_COLOR_TEXT = "Background Color"

SELECT_COLOR_TEXT = "Select"

class Dialog(QDialog):

	def User(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.User = color.name()
			self.userLabel.setText(f"<font color=\"{self.Colors.User}\">{USER_COLOR_TEXT}</font>")

	def coSelf(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Self = color.name()
			self.selfLabel.setText(f"<font color=\"{self.Colors.User}\">{SELF_COLOR_TEXT}</font>")

	def Action(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Action = color.name()
			self.actionLabel.setText(f"<font color=\"{self.Colors.Action}\">{ACTION_COLOR_TEXT}</font>")

	def Notify(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Notify = color.name()
			self.notifyLabel.setText(f"<font color=\"{self.Colors.Notify}\">{NOTIFY_COLOR_TEXT}</font>")

	def Channel(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Channel = color.name()
			self.channelLabel.setText(f"<font color=\"{self.Colors.Channel}\">{CHANNEL_COLOR_TEXT}</font>")

	def Notice(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Notice = color.name()
			self.noticeLabel.setText(f"<font color=\"{self.Colors.Notice}\">{NOTICE_COLOR_TEXT}</font>")

	def Normal(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Normal = color.name()
			self.normalLabel.setText(f"<font color=\"{self.Colors.Normal}\">{NORMAL_COLOR_TEXT}</font>")

	def Background(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.Colors.Background = color.name()
			self.backgroundLabel.setText(f"<font color=\"{self.Colors.Background}\">{BACKGROUND_COLOR_TEXT}</font>")

	def Save(self):
		saveColorSettings(self.Colors,COLOR_FILE)
		self.close()

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.setWindowTitle(f"Colors")
		self.setWindowIcon(QIcon(USER_ICON))

		self.Colors = loadColorSettings(COLOR_FILE)

		# User Name Color
		userLayout = QHBoxLayout()
		self.userLabel = QLabel(f"<font color=\"{self.Colors.User}\">{USER_COLOR_TEXT}</font>")
		self.cUser = QPushButton(SELECT_COLOR_TEXT)
		self.cUser.clicked.connect(self.User)
		userLayout.addWidget(self.userLabel)
		userLayout.addWidget(self.cUser)

		# Self Color
		selfLayout = QHBoxLayout()
		self.selfLabel = QLabel(f"<font color=\"{self.Colors.Self}\">{SELF_COLOR_TEXT}</font>")
		self.cSelf = QPushButton(SELECT_COLOR_TEXT)
		self.cSelf.clicked.connect(self.coSelf)
		selfLayout.addWidget(self.selfLabel)
		selfLayout.addWidget(self.cSelf)

		# Action Color
		actionLayout = QHBoxLayout()
		self.actionLabel = QLabel(f"<font color=\"{self.Colors.Action}\">{ACTION_COLOR_TEXT}</font>")
		self.cAction = QPushButton(SELECT_COLOR_TEXT)
		self.cAction.clicked.connect(self.Action)
		actionLayout.addWidget(self.actionLabel)
		actionLayout.addWidget(self.cAction)

		# Notify Color
		notifyLayout = QHBoxLayout()
		self.notifyLabel = QLabel(f"<font color=\"{self.Colors.Action}\">{NOTIFY_COLOR_TEXT}</font>")
		self.cNotify = QPushButton(SELECT_COLOR_TEXT)
		self.cNotify.clicked.connect(self.Notify)
		notifyLayout.addWidget(self.notifyLabel)
		notifyLayout.addWidget(self.cNotify)

		# Channel Color
		channelLayout = QHBoxLayout()
		self.channelLabel = QLabel(f"<font color=\"{self.Colors.Channel}\">{CHANNEL_COLOR_TEXT}</font>")
		self.cChannel = QPushButton(SELECT_COLOR_TEXT)
		self.cChannel.clicked.connect(self.Channel)
		channelLayout.addWidget(self.channelLabel)
		channelLayout.addWidget(self.cChannel)

		# Notice Color
		noticeLayout = QHBoxLayout()
		self.noticeLabel = QLabel(f"<font color=\"{self.Colors.Notice}\">{NOTICE_COLOR_TEXT}</font>")
		self.cNotice = QPushButton(SELECT_COLOR_TEXT)
		self.cNotice.clicked.connect(self.Notice)
		noticeLayout.addWidget(self.noticeLabel)
		noticeLayout.addWidget(self.cNotice)

		# Normal Color
		normalLayout = QHBoxLayout()
		self.normalLabel = QLabel(f"<font color=\"{self.Colors.Normal}\">{NORMAL_COLOR_TEXT}</font>")
		self.cNormal = QPushButton(SELECT_COLOR_TEXT)
		self.cNormal.clicked.connect(self.Normal)
		normalLayout.addWidget(self.normalLabel)
		normalLayout.addWidget(self.cNormal)

		# Background Color
		backgroundLayout = QHBoxLayout()
		self.backgroundLabel = QLabel(f"<font color=\"{self.Colors.Background}\">{BACKGROUND_COLOR_TEXT}</font>")
		self.cBackground = QPushButton(SELECT_COLOR_TEXT)
		self.cBackground.clicked.connect(self.Background)
		backgroundLayout.addWidget(self.backgroundLabel)
		backgroundLayout.addWidget(self.cBackground)


		self.saveColors = QPushButton("Save")
		self.saveColors.clicked.connect(self.Save)

		self.canc = QPushButton("Cancel")
		self.canc.clicked.connect(self.close)

		expl = QLabel("Some color changes will only take effect after restarting the client.")

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(expl)
		finalLayout.addLayout(userLayout)
		finalLayout.addLayout(selfLayout)
		finalLayout.addLayout(actionLayout)
		finalLayout.addLayout(notifyLayout)
		finalLayout.addLayout(channelLayout)
		finalLayout.addLayout(noticeLayout)
		finalLayout.addLayout(normalLayout)
		finalLayout.addLayout(backgroundLayout)
		finalLayout.addWidget(self.saveColors)
		finalLayout.addWidget(self.canc)

		self.setLayout(finalLayout)
