
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

import sys
import os

from PyQt5.QtWidgets import *

from PyQt5.QtCore import *

from quirc.gui.main import Quirc

from quirc.common import *
from quirc.style import *

def restart_program():
	"""Restarts the current program.
	Note: this function does not return. Any cleanup action (like
	saving data) must be done before calling this function."""
	python = sys.executable
	os.execl(python, python, * sys.argv)

if __name__ == '__main__':

	GUI_WINDOW_STYLE = "Windows"

	app = QApplication(sys.argv)

	iconStyle = BiggerIconsStyle(GUI_WINDOW_STYLE)
	app.setStyle(iconStyle)

	with open(RESOURCE_STYLE_SHEET,"r") as fh:
		app.setStyleSheet(fh.read())

	Quirc_IRC_Client = Quirc(app,restart_program)
	Quirc_IRC_Client.qtStyle = GUI_WINDOW_STYLE
	Quirc_IRC_Client.show()

	app.exec_()
