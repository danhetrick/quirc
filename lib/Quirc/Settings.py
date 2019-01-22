
import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

USER_NAME_COLOR = "#0000FF"
SELF_NAME_COLOR = "#FF0000"
ACTION_MESSAGE_COLOR = "#008000"
NOTIFICATION_MESSAGE_COLOR = "#708090"
CHANNEL_MESSAGE_COLOR = "#FFA500"
NOTICE_MESSAGE_COLOR = "#800080"
NORMAL_TEXT_COLOR = "#000000"

COLOR_URL_LINKS = False
URL_LINK_COLOR = "#0000FF"

MAXIMUM_IRC_MESSAGE_LENGTH = 450
MAXIMUM_NICK_DISPLAY_SIZE = 12

INSTALL_DIRECTORY = sys.path[0]
RESOURCE_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "resources")
ICON_DIRECTORY = os.path.join(RESOURCE_DIRECTORY, "icons")
FONT_DIRECTORY = os.path.join(RESOURCE_DIRECTORY, "fonts")
IMAGE_DIRECTORY = os.path.join(RESOURCE_DIRECTORY, "images")
CONFIG_DIRECTORY = os.path.join(INSTALL_DIRECTORY, "config")

BACKGROUND = os.path.join(IMAGE_DIRECTORY, "background.png")
LOGO = os.path.join(IMAGE_DIRECTORY, "quirc.png")

CASCADE_ICON = os.path.join(ICON_DIRECTORY, "cascade.png")
TILE_ICON = os.path.join(ICON_DIRECTORY, "tile.png")
QUIRC_ICON = os.path.join(ICON_DIRECTORY, "quirc.png")
CHAT_ICON = os.path.join(ICON_DIRECTORY, "chat.png")
SERVER_ICON = os.path.join(ICON_DIRECTORY, "server.png")
USER_ICON = os.path.join(ICON_DIRECTORY, "user.png")
STAR_ICON = os.path.join(ICON_DIRECTORY, "star.png")
HASH_ICON = os.path.join(ICON_DIRECTORY, "hash.png")
CONNECT_ICON = os.path.join(ICON_DIRECTORY, "connect.png")
EXIT_ICON = os.path.join(ICON_DIRECTORY, "exit.png")
DISCONNECT_ICON = os.path.join(ICON_DIRECTORY, "disconnect.png")

MSG_CHAT = "chat.png"
MSG_USER = "user.png"
MSG_STAR = "star.png"
MSG_HASH = "hash.png"
MSG_QUIRC = "quirc16.png"

FIRACODE_FONT_LOCATION = os.path.join(FONT_DIRECTORY, "FiraCode-Regular.ttf")
FIRACODE_BOLD_FONT_LOCATION = os.path.join(FONT_DIRECTORY, "FiraCode-Bold.ttf")
DEFAULT_FONT_SIZE = 10
TITLE_FONT_SIZE = 10

STORED_SERVER_FILE = os.path.join(RESOURCE_DIRECTORY, "servers.txt")
USER_INFORMATION_FILE = os.path.join(CONFIG_DIRECTORY, "user.json")

id = QFontDatabase.addApplicationFont(FIRACODE_FONT_LOCATION)
_fontstr = QFontDatabase.applicationFontFamilies(id)[0]
QUIRC_FONT = QFont(_fontstr, DEFAULT_FONT_SIZE)

QUIRC_TITLE_FONT = QFont(_fontstr, TITLE_FONT_SIZE)

id = QFontDatabase.addApplicationFont(FIRACODE_BOLD_FONT_LOCATION)
_fontstr = QFontDatabase.applicationFontFamilies(id)[0]
QUIRC_FONT_BOLD = QFont(_fontstr, DEFAULT_FONT_SIZE)
QUIRC_FONT_BOLD.setBold(True)

T_NORMAL_COLOR = "!NORMAL!"
T_USER = "!USER!"
T_MESSAGE = "!MESSAGE!"
T_TIME = "!TIME!"
T_ICON = "!I!"
T_COLOR = "!COLOR!"

CHAT_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
    <tr>
      <td style="width: 150px; height: 20px; text-align: right; vertical-align: top;"><font color="!COLOR!">!USER!</font></td>
      <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!NORMAL!">!MESSAGE!</font></td>
    </tr>
  </tbody>
</table>
"""

CHAT_TIMESTAMP_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
    <tr>
      <td style="width: 75px; height: 20px; text-align: center; vertical-align: top;">!TIME!</td>
      <td style="width: 150px; text-align: right; vertical-align: top;"><font color="!COLOR!">!USER!</font></td>
      <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!NORMAL!">!MESSAGE!</font></td>
    </tr>
  </tbody>
</table>
"""

CHAT_ICON_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
    <tr>
      <td style="width: 20px; height: 20px; text-align: center; vertical-align: top;"><img src="!I!"></td>
      <td style="text-align: right; vertical-align: top;"><font color="!COLOR!">&nbsp;!USER!</font></td>
      <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!NORMAL!">!MESSAGE!</font></td>
    </tr>
  </tbody>
</table>
"""

CHAT_ICON_TIMESTAMP_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
    <tr>
      <td style="width: 75px; height: 20px; text-align: center; vertical-align: top;">!TIME!</td>
      <td style="width: 20px; height: 20px; text-align: center; vertical-align: top;"><img src="!I!"></td>
      <td style="text-align: right; vertical-align: top;"><font color="!COLOR!">&nbsp;!USER!</font></td>
      <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!NORMAL!">!MESSAGE!</font></td>
    </tr>
  </tbody>
</table>
"""

MESSAGE_ICON_TEMPLATE = """
<table style="width: 100%;" border="0">
  <tbody>
    <tr>
      <td style="width: 20px; height: 20px; text-align: center; vertical-align: top;"><img src="!I!"></td>
      <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!COLOR!"><b>!MESSAGE!</b></font></td>
    </tr>
  </tbody>
</table>
"""

MESSAGE_ICON_TIMESTAMP_TEMPLATE = """
<table style="width: 100%;" border="0">
      <tbody>
        <tr>
          <td style="width: 75px; height: 20px; text-align: center; vertical-align: top;">!TIME!</td>
          <td style="width: 20px; height: 20px; text-align: center; vertical-align: top;"><img src="!I!"></td>
          <td style="text-align: left; vertical-align: top;">&nbsp;<font color="!COLOR!"><b>!MESSAGE!</b></font></td>
        </tr>
      </tbody>
    </table>
"""
