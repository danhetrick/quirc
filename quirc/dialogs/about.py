
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

		#self.setWindowTitle(f"About {APPLICATION_NAME}")
		self.setWindowIcon(QIcon(QUIRC_ICON))

		boldfont = self.font()
		boldfont.setBold(True)
		boldfont.setPointSize(12)

		boldsmaller = self.font()
		boldsmaller.setBold(True)
		boldsmaller.setPointSize(8)

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

		twisted_image = QLabel()
		pixmap = QPixmap(TWISTED_IMAGE)
		twisted_image.setPixmap(pixmap)
		twisted_image.setAlignment(Qt.AlignCenter)

		icons8_image = QLabel()
		pixmap = QPixmap(ICONS8_IMAGE)
		icons8_image.setPixmap(pixmap)
		icons8_image.setAlignment(Qt.AlignCenter)

		

		pyBox = QVBoxLayout()
		pyBox.addWidget(python_image)
		pyLink = QLabel("<a href=\"https://www.python.org/\">Python</a>")
		pyLink.setAlignment(Qt.AlignCenter)
		pyBox.addWidget(pyLink)
		pyLink.setFont(boldsmaller)
		pyLink.setOpenExternalLinks(True)


		gplBox = QVBoxLayout()
		gplBox.addWidget(gpl_image)
		gplLink = QLabel("<a href=\"https://www.gnu.org/\">Gnu</a>")
		gplLink.setAlignment(Qt.AlignCenter)
		gplBox.addWidget(gplLink)
		gplLink.setFont(boldsmaller)
		gplLink.setOpenExternalLinks(True)

		qtBox = QVBoxLayout()
		qtBox.addWidget(qt_image)
		qtLink = QLabel("<a href=\"https://www.qt.io/\">Qt</a>")
		qtLink.setAlignment(Qt.AlignCenter)
		qtBox.addWidget(qtLink)
		qtLink.setFont(boldsmaller)
		qtLink.setOpenExternalLinks(True)

		twistBox = QVBoxLayout()
		twistBox.addWidget(twisted_image)
		twistLink = QLabel("<a href=\"https://twistedmatrix.com\">Twisted</a>")
		twistLink.setAlignment(Qt.AlignCenter)
		twistBox.addWidget(twistLink)
		twistLink.setFont(boldsmaller)
		twistLink.setOpenExternalLinks(True)

		icons8Box = QVBoxLayout()
		icons8Box.addWidget(icons8_image)
		icons8Link = QLabel("<a href=\"https://icons8.com/\">Icons8</a>")
		icons8Link.setAlignment(Qt.AlignCenter)
		icons8Box.addWidget(icons8Link)
		icons8Link.setFont(boldsmaller)
		icons8Link.setOpenExternalLinks(True)

		technology = QHBoxLayout()
		technology.addLayout(pyBox)
		technology.addLayout(twistBox)
		technology.addLayout(icons8Box)
		technology.addLayout(qtBox)
		technology.addLayout(gplBox)


		# technology = QVBoxLayout()
		# technology.addLayout(technology1)
		# technology.addLayout(gplBox)


		dinfo = QLabel(f"Open Source Internet Relay Chat Client")
		dinfo.setAlignment(Qt.AlignCenter)
		dinfo.setFont(boldfont)

		ainfo = QLabel(f"Version {APPLICATION_VERSION}")
		ainfo.setAlignment(Qt.AlignCenter)
		ainfo.setFont(boldfont)

		ilink = QLabel("<a href=\"https://github.com/danhetrick/quirc\">Quirc GitHub Repository</a>")
		ilink.setAlignment(Qt.AlignCenter)
		ilink.setOpenExternalLinks(True)
		ilink.setFont(boldsmaller)

		# irclib = QLabel("<a href=\"https://twistedmatrix.com\">Twisted</a> by Twisted Matrix Labs")
		# irclib.setAlignment(Qt.AlignCenter)
		# irclib.setOpenExternalLinks(True)

		colourlib = QLabel("<a href=\"https://github.com/vaab/colour\">Python Colour Library</a> by Valentin Lab")
		colourlib.setAlignment(Qt.AlignCenter)
		colourlib.setOpenExternalLinks(True)
		colourlib.setFont(boldsmaller)

		# icons = QLabel("Icons by <a href=\"https://icons8.com/icons\">Icons8</a>")
		# icons.setAlignment(Qt.AlignCenter)
		# icons.setOpenExternalLinks(True)

		spacer = QLabel(" ")

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(logo)
		finalLayout.addWidget(dinfo)
		finalLayout.addWidget(ainfo)
		#finalLayout.addWidget(spacer)
		#finalLayout.addWidget(irclib)
		#finalLayout.addWidget(icons)
		#finalLayout.addWidget(spacer)
		finalLayout.addLayout(technology)
		finalLayout.addWidget(colourlib)
		finalLayout.addWidget(ilink)
		#finalLayout.addLayout(gplBox)
		#finalLayout.addWidget(spacer)
		

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)

		self.setFixedSize(400, 300)
