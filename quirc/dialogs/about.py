
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

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.setWindowTitle(f"About {APPLICATION_NAME}")
		self.setWindowIcon(QIcon(ABOUT_ICON))

		logo = QLabel()
		pixmap = QPixmap(LOGO_IMAGE)
		logo.setPixmap(pixmap)
		logo.setAlignment(Qt.AlignCenter)

		qt_image = QLabel()
		pixmap = QPixmap(QT_IMAGE)
		qt_image.setPixmap(pixmap)
		qt_image.setAlignment(Qt.AlignCenter)

		python_image = QLabel()
		pixmap = QPixmap(PYTHON_IMAGE)
		python_image.setPixmap(pixmap)
		python_image.setAlignment(Qt.AlignCenter)

		gpl_image = QLabel()
		pixmap = QPixmap(GPL_IMAGE)
		gpl_image.setPixmap(pixmap)
		gpl_image.setAlignment(Qt.AlignCenter)

		technology = QHBoxLayout()
		technology.addWidget(python_image)
		technology.addWidget(gpl_image)
		technology.addWidget(qt_image)

		dinfo = QLabel(f"A Python/Qt Internet Relay Chat Client")
		dinfo.setAlignment(Qt.AlignCenter)

		ainfo = QLabel(f"Version {APPLICATION_VERSION}")
		ainfo.setAlignment(Qt.AlignCenter)

		ilink = QLabel("<a href=\"https://github.com/danhetrick\">https://github.com/danhetrick</a>")
		ilink.setAlignment(Qt.AlignCenter)
		ilink.setOpenExternalLinks(True)

		irclib = QLabel("<a href=\"https://twistedmatrix.com\">Twisted</a> by Twisted Matrix Labs")
		irclib.setAlignment(Qt.AlignCenter)
		irclib.setOpenExternalLinks(True)

		colourlib = QLabel("<a href=\"https://github.com/vaab/colour\">Python Colour Library</a> by Valentin Lab")
		colourlib.setAlignment(Qt.AlignCenter)
		colourlib.setOpenExternalLinks(True)

		icons = QLabel("Icons by <a href=\"https://icons8.com/icons\">Icons8</a>")
		icons.setAlignment(Qt.AlignCenter)
		icons.setOpenExternalLinks(True)

		spacer = QLabel(" ")

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(logo)
		finalLayout.addWidget(dinfo)
		finalLayout.addWidget(ainfo)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(irclib)
		finalLayout.addWidget(colourlib)
		finalLayout.addWidget(icons)
		finalLayout.addWidget(spacer)
		finalLayout.addLayout(technology)
		finalLayout.addWidget(spacer)
		finalLayout.addWidget(ilink)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
