
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

	def __init__(self,info,parent=None):
		super(Dialog,self).__init__(parent)

		self.info = info

		topic = parent.topic

		channel_name = info[CHANNEL_INFO_NAME]
		channel_key = info[CHANNEL_INFO_KEY]
		channel_limit = info[CHANNEL_INFO_LIMIT]
		channel_invite_only = info[CHANNEL_INFO_INVITEONLY]
		channel_allow_external = info[CHANNEL_INFO_ALLOWEXTERNAL]
		channel_topic_locked = info[CHANNEL_INFO_TOPICLOCKED]
		channel_protected = info[CHANNEL_INFO_PROTECTED]
		channel_secret = info[CHANNEL_INFO_SECRET]
		channel_moderated = info[CHANNEL_INFO_MODERATED]
		channel_nocolors = info[CHANNEL_INFO_NOCOLORS]

		self.setWindowTitle(f"{channel_name}")

		self.setFont(parent.parent.default_font)

		self.title = QLabel(f"<font color=\"{QUIRC_COLOR}\">{channel_name}</font>")
		self.title.setFont(parent.parent.bold_huge_font)

		cTitle = QHBoxLayout()
		cTitle.addStretch()
		cTitle.addWidget(self.title)
		cTitle.addStretch()


		cPrivs = QHBoxLayout()
		privs = QLabel()
		pixmap = QPixmap(RESOURCE_IMAGE_USER).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
		privs.setPixmap(pixmap)
		if parent.is_op:
			cPrivs.addWidget(QLabel("You're a channel operator"))
		elif parent.voiced:
			cPrivs.addWidget(QLabel("You're a voiced user"))
		else:
			cPrivs.addWidget(QLabel("You're a normal user"))
		cPrivs.addStretch()
		cPrivs.addWidget(privs)

		cKey = QHBoxLayout()
		privs = QLabel()
		if len(channel_key)>0:
			pixmap = QPixmap(RESOURCE_IMAGE_LOCKED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cKey.addWidget(QLabel(f"Locked with channel key <b>{channel_key}</b>"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_UNLOCKED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cKey.addWidget(QLabel("No channel key"))
		cKey.addStretch()
		cKey.addWidget(privs)

		cLimit = QHBoxLayout()
		privs = QLabel()
		if channel_limit>0:
			pixmap = QPixmap(RESOURCE_IMAGE_LIMIT).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cLimit.addWidget(QLabel(f"Channel limited to {str(channel_limit)} users"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_NOLIMIT).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cLimit.addWidget(QLabel("No user limit"))
		cLimit.addStretch()
		cLimit.addWidget(privs)

		cInvite = QHBoxLayout()
		privs = QLabel()
		if channel_invite_only==1:
			pixmap = QPixmap(RESOURCE_IMAGE_INVITEONLY).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cInvite.addWidget(QLabel(f"Invite only"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_LIMIT).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cInvite.addWidget(QLabel("Anyone can join"))
		cInvite.addStretch()
		cInvite.addWidget(privs)

		cExtern = QHBoxLayout()
		privs = QLabel()
		if channel_allow_external==1:
			pixmap = QPixmap(RESOURCE_IMAGE_NOEXTERNAL).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cExtern.addWidget(QLabel(f"No external messaged"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_EXTERNAL).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cExtern.addWidget(QLabel("External messages allowed"))
		cExtern.addStretch()
		cExtern.addWidget(privs)

		cTopic = QHBoxLayout()
		privs = QLabel()
		if channel_topic_locked==1:
			pixmap = QPixmap(RESOURCE_IMAGE_LOCKED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cTopic.addWidget(QLabel(f"Topic can be changed by operators"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_UNLOCKED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cTopic.addWidget(QLabel("Anyone can change the topic"))
		cTopic.addStretch()
		cTopic.addWidget(privs)

		cProtect = QHBoxLayout()
		privs = QLabel()
		if channel_protected==1:
			pixmap = QPixmap(RESOURCE_IMAGE_PLUS).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cProtect.addWidget(QLabel(f"Private"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_MINUS).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cProtect.addWidget(QLabel("Not private"))
		cProtect.addStretch()
		cProtect.addWidget(privs)

		cSecret = QHBoxLayout()
		privs = QLabel()
		if channel_secret==1:
			pixmap = QPixmap(RESOURCE_IMAGE_SECRET).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cSecret.addWidget(QLabel(f"Channel is secret"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_NOTSECRET).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cSecret.addWidget(QLabel("Channel is not secret"))
		cSecret.addStretch()
		cSecret.addWidget(privs)

		cMods = QHBoxLayout()
		privs = QLabel()
		if channel_moderated==1:
			pixmap = QPixmap(RESOURCE_IMAGE_MODERATED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cMods.addWidget(QLabel(f"Channel is moderated"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_UNMODERATED).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cMods.addWidget(QLabel("Channel is unmoderated"))
		cMods.addStretch()
		cMods.addWidget(privs)

		cColors = QHBoxLayout()
		privs = QLabel()
		if channel_nocolors==1:
			pixmap = QPixmap(RESOURCE_IMAGE_NO).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cColors.addWidget(QLabel(f"Channel strips all color codes"))
		else:
			pixmap = QPixmap(RESOURCE_IMAGE_COLORS).scaled(QSize(20,20),transformMode=Qt.SmoothTransformation)
			privs.setPixmap(pixmap)
			cColors.addWidget(QLabel("Color codes allowed"))
		cColors.addStretch()
		cColors.addWidget(privs)

		infoLayout = QVBoxLayout()
		infoLayout.addLayout(cTitle)
		infoLayout.addLayout(cPrivs)
		infoLayout.addLayout(cKey)
		infoLayout.addLayout(cLimit)
		infoLayout.addLayout(cInvite)
		infoLayout.addLayout(cExtern)
		infoLayout.addLayout(cProtect)
		infoLayout.addLayout(cSecret)
		infoLayout.addLayout(cMods)
		infoLayout.addLayout(cColors)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(infoLayout)