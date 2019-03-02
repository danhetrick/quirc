
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

class Dialog(QMainWindow):

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.disp = QTextBrowser(self)

		self.setCentralWidget(self.disp)

	def openHTML(self,file,title):
		f = open(file, "r")
		content = f.read()

		self.disp.setHtml(content)
		self.setWindowTitle(title)


