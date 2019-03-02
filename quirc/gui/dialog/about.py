
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

class Window(QDialog):
	
	def __init__(self,parent=None):
		super(Window,self).__init__(parent)

		self.setWindowTitle(f"About {APPLICATION_NAME}")
		self.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))

		nbmedium_font = parent.userlist_font

		medium_font = parent.bold_userlist_font

		small_font = parent.default_font

		logo = QLabel()
		pixmap = QPixmap(RESOURCE_LOGO_300x100)
		logo.setPixmap(pixmap)
		logo.setAlignment(Qt.AlignCenter)

		qapp = QLabel("Quirc is pronounced /kwɜrk/")
		qapp.setFont(nbmedium_font)
		qapp.setAlignment(Qt.AlignCenter)

		dapp = QLabel(f"{APPLICATION_DESCRIPTION}")
		dapp.setFont(medium_font)
		dapp.setAlignment(Qt.AlignCenter)

		uapp = QLabel("<a href=\"https://github.com/danhetrick/quirc\">https://github.com/danhetrick/quirc</a>")
		uapp.setAlignment(Qt.AlignCenter)
		uapp.setFont(medium_font)
		uapp.setOpenExternalLinks(True)

		gpl_logo = QLabel()
		pixmap = QPixmap(RESOURCE_GPL_LOGO)
		gpl_logo.setPixmap(pixmap)
		gpl_logo.setAlignment(Qt.AlignCenter)

		py_logo = QLabel()
		pixmap = QPixmap(RESOURCE_PYTHON_LOGO)
		py_logo.setPixmap(pixmap)
		py_logo.setAlignment(Qt.AlignCenter)

		qt_logo = QLabel()
		pixmap = QPixmap(RESOURCE_QT_LOGO)
		qt_logo.setPixmap(pixmap)
		qt_logo.setAlignment(Qt.AlignCenter)

		technology = QHBoxLayout()
		technology.addWidget(py_logo)
		technology.addWidget(gpl_logo)
		technology.addWidget(qt_logo)

		ufont = QLabel("<a href=\"https://github.com/tonsky/FiraCode\">Fira Code Font</a> by <a href=\"https://twitter.com/nikitonsky\">Nikita Prokopov</a>")
		ufont.setAlignment(Qt.AlignCenter)
		ufont.setFont(small_font)
		ufont.setOpenExternalLinks(True)

		ulib = QLabel("<a href=\"https://github.com/jaraco/irc\">Python IRC Library</a> by <a href=\"mailto:jaraco@jaraco.com\">Jason R. Coombs</a>")
		ulib.setAlignment(Qt.AlignCenter)
		ulib.setFont(small_font)
		ulib.setOpenExternalLinks(True)

		clib = QLabel("<a href=\"https://github.com/vaab/colour\">Python Colour Library</a> by Valentin Lab")
		clib.setAlignment(Qt.AlignCenter)
		clib.setFont(small_font)
		clib.setOpenExternalLinks(True)

		cicon = QLabel("<a href=\"https://github.com/google/material-design-icons\">Icons</a> by <a href=\"http://google.com\">Google</a>")
		cicon.setAlignment(Qt.AlignCenter)
		cicon.setFont(small_font)
		cicon.setOpenExternalLinks(True)

		# cversion = QLabel(f"{APPLICATION_NAME} {APPLICATION_VERSION} on {HOST_OS} {HOST_OS_VERSION}")
		# cversion.setAlignment(Qt.AlignCenter)
		# cversion.setFont(small_font)

		aexit = QPushButton("Ok")
		aexit.clicked.connect(self.close)

		spacer = QLabel(" ")

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(logo)
		finalLayout.addWidget(qapp)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(dapp)
		finalLayout.addWidget(uapp)
		#finalLayout.addWidget(cversion)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(ulib)
		finalLayout.addWidget(clib)
		finalLayout.addWidget(ufont)
		finalLayout.addWidget(cicon)
		finalLayout.addWidget(spacer)
		finalLayout.addLayout(technology)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(aexit)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)