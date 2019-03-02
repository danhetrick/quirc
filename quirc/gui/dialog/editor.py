
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

from quirc.script import QuircScriptThread
from quirc.script import Script

from quirc.code_edit import QCodeEditor

class Dialog(QMainWindow):

	def closeEvent(self,event):
		self.parent.editorWindow = None
		self.parent.editorSubWindow.close()
		self.close()

	def newFile(self):
		self.FILENAME = ''
		self.actSave.setEnabled(False)
		self.errors.setText('')
		self.editor.setPlainText('')
		self.setWindowTitle("QScript")

	def saveDialog(self):
		script = open(self.FILENAME,"w")
		script.write(self.editor.toPlainText())

	def saveAsDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Quirc Script As...",INSTALL_DIRECTORY,"Quirc Script Files (*.quirc);;Text Files (*.txt);;All Files (*)", options=options)
		if fileName:
			self.FILENAME = fileName
			if '.' in fileName:
				pass
			else:
				self.FILENAME = self.FILENAME + '.quirc'
			self.actSave.setEnabled(True)
			self.setWindowTitle(f"QScript - {self.FILENAME}")
			script = open(self.FILENAME,"w")
			script.write(self.editor.toPlainText())

	def openDialog(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"Open Quirc Script", INSTALL_DIRECTORY,"Quirc Script Files (*.quirc);;Text Files (*.txt);;All Files (*)", options=options)
		if fileName:
			script = open(fileName,"r")
			# self.editor.setText(script.read())
			self.editor.setPlainText(script.read())
			self.FILENAME = fileName
			self.actSave.setEnabled(True)
			self.setWindowTitle(f"QScript - {fileName}")

	def runScript(self):
		# rt = Script(self.CLIENT,self.GUI,self.editor.toPlainText())
		# rt.channel("#quirc")
		# rt.exec()
		if self.parent.online:
			self.errors.setText('')
			self.qscript = QuircScriptThread(self.parent.irc.connection,self.parent,self.editor.toPlainText(),RUN_SCRIPT)
			self.qscript.closewindow.connect(self.close_window)
			self.qscript.channelmsg.connect(self.channel_msg)
			self.qscript.errormsg.connect(self.error_msg)
			self.qscript.start()
		else:
			#print("NOT ONLINE!")
			self.error_dialog = QErrorMessage()
			self.error_dialog.showMessage("Not connected to IRC.")
			self.errors.setText('')
			self.errors.append(f"Not connected to IRC.")

	def testScript(self):
		self.errors.setText('')
		self.qscript = QuircScriptThread(self,self.parent,self.editor.toPlainText(),TEST_SCRIPT)
		#self.qscript.closewindow.connect(self.close_window)
		#self.qscript.channelmsg.connect(self.channel_msg)
		self.qscript.errormsg.connect(self.error_msg)
		self.qscript.start()

	@pyqtSlot(str)
	def close_window(self,data):
		self.parent.partChannel(data)

	@pyqtSlot(list)
	def channel_msg(self,data):
		channel = data[0]
		msg = data[1]

		if channel.lower() == "server":
			self.parent.serverWindow.writeText(msg)
			return

		if channel.lower() == "console":
			print(msg)
			return
		
		self.parent.writeToChannel(channel,msg)

	@pyqtSlot(list)
	def error_msg(self,data):
		line = data[0]
		msg = data[1]

		if line == "0":
			self.errors.append(f"{msg}")
		else:
			self.errors.append(f"Line {line}: {msg}")

	def __init__(self,parent=None):
		super(Dialog,self).__init__(parent)

		self.parent = parent

		self.FILENAME = ''

		#self.editor = QTextEdit(self)

		self.editor = QCodeEditor(self)
		self.errors = QTextEdit(self)

		self.editor.setFont(parent.userlist_font)
		self.errors.setFont(parent.userlist_font)

		self.errors.setStyleSheet("QTextEdit { background-color: lightgray; };")
		self.errors.setReadOnly(True)

		##################################

		self.vsplit = QSplitter(Qt.Vertical)
		self.vsplit.addWidget(self.editor)
		self.vsplit.addWidget(self.errors)
		self.vsplit.setSizes([400,100])

		self.setCentralWidget(self.vsplit)


		##################################

		#self.editor.setFont(QUIRC_FONT)

		#self.setCentralWidget(self.editor)

		self.highlighter = Highlighter(self.editor.document())

		self.setWindowTitle("QScript")
		#self.setWindowIcon(QIcon(RESOURCE_ICON_QUIRC))

		self.resize(500,500)

		menubar = self.menuBar()

		fileMenu = menubar.addMenu("File")

		self.actNew = QAction(QIcon(RESOURCE_IMAGE_NEWFILE),"New",self)
		self.actNew.setShortcut('Ctrl+N')
		self.actNew.setStatusTip('Create a new script')
		self.actNew.triggered.connect(self.newFile)
		fileMenu.addAction(self.actNew)

		self.actOpen = QAction(QIcon(RESOURCE_IMAGE_FILE),"Open",self)
		self.actOpen.setShortcut('Ctrl+O')
		self.actOpen.setStatusTip('Open a script')
		self.actOpen.triggered.connect(self.openDialog)
		fileMenu.addAction(self.actOpen)

		self.actSave = QAction(QIcon(RESOURCE_IMAGE_SAVE),"Save",self)
		self.actSave.setShortcut('Ctrl+S')
		self.actSave.setStatusTip('Save script')
		self.actSave.triggered.connect(self.saveDialog)
		self.actSave.setEnabled(False)
		fileMenu.addAction(self.actSave)

		self.actSaveAs = QAction(QIcon(RESOURCE_IMAGE_SAVE),"Save As...",self)
		self.actSaveAs.triggered.connect(self.saveAsDialog)
		fileMenu.addAction(self.actSaveAs)

		fileMenu.addSeparator()

		self.actQuit = QAction(QIcon(RESOURCE_ICON_EXIT),"Exit",self)
		self.actQuit.setShortcut('Ctrl+Q')
		self.actQuit.setStatusTip('Exit editor')
		self.actQuit.triggered.connect(self.close)
		fileMenu.addAction(self.actQuit)



		editMenu = menubar.addMenu("Edit")

		self.actUndo = QAction(QIcon(RESOURCE_IMAGE_UNDO),"Undo",self)
		self.actUndo.setShortcut('Ctrl+Y')
		self.actUndo.setStatusTip('Undo last action')
		self.actUndo.triggered.connect(self.editor.undo)
		editMenu.addAction(self.actUndo)

		self.actRedo = QAction(QIcon(RESOURCE_IMAGE_REDO),"Redo",self)
		self.actRedo.setShortcut('Ctrl+Z')
		self.actRedo.setStatusTip('Redo last undo')
		self.actRedo.triggered.connect(self.editor.redo)
		editMenu.addAction(self.actRedo)

		editMenu.addSeparator()

		self.actCut = QAction(QIcon(RESOURCE_IMAGE_CUT),"Cut",self)
		self.actCut.setShortcut('Ctrl+X')
		self.actCut.triggered.connect(self.editor.cut)
		editMenu.addAction(self.actCut)

		self.actCopy = QAction(QIcon(RESOURCE_IMAGE_COPY),"Copy",self)
		self.actCopy.setShortcut('Ctrl+C')
		self.actCopy.triggered.connect(self.editor.copy)
		editMenu.addAction(self.actCopy)

		self.actPaste = QAction(QIcon(RESOURCE_IMAGE_PASTE),"Paste",self)
		self.actPaste.setShortcut('Ctrl+V')
		self.actPaste.triggered.connect(self.editor.paste)
		editMenu.addAction(self.actPaste)

		editMenu.addSeparator()

		# myWidget.setFont(QFontDialog.getFont(0, myWidget.font()))

		self.actFont = QAction(QIcon(RESOURCE_IMAGE_FONT),"Font",self)
		self.actFont.triggered.connect(self.doFont)
		editMenu.addAction(self.actFont)


		scriptMenu = menubar.addMenu("Script")

		self.actTest = QAction(QIcon(RESOURCE_IMAGE_BUG),"Check for errors",self)
		self.actTest.triggered.connect(self.testScript)
		scriptMenu.addAction(self.actTest)

		self.actRun = QAction(QIcon(RESOURCE_IMAGE_RUN),"Run",self)
		self.actRun.setShortcut('Ctrl+R')
		self.actRun.setStatusTip('Execute script')
		self.actRun.triggered.connect(self.runScript)
		scriptMenu.addAction(self.actRun)

		scriptMenu.addSeparator()

		snippetsMenu = scriptMenu.addMenu("Command Templates")

		self.cmdJoin = QAction("Join channel",self)
		self.cmdJoin.triggered.connect(self.injectJoin)
		snippetsMenu.addAction(self.cmdJoin)

		self.cmdJoin = QAction("Join channel with key",self)
		self.cmdJoin.triggered.connect(self.injectJoinKey)
		snippetsMenu.addAction(self.cmdJoin)

		self.cmdPart = QAction("Part channel",self)
		self.cmdPart.triggered.connect(self.injectPart)
		snippetsMenu.addAction(self.cmdPart)

		self.cmdWriteConsole = QAction("Write to console",self)
		self.cmdWriteConsole.triggered.connect(self.injectWriteConsole)
		snippetsMenu.addAction(self.cmdWriteConsole)

		self.cmdWriteServer = QAction("Write to server window",self)
		self.cmdWriteServer.triggered.connect(self.injectWriteServer)
		snippetsMenu.addAction(self.cmdWriteServer)

		self.cmdWriteChannel = QAction("Write to channel window",self)
		self.cmdWriteChannel.triggered.connect(self.injectWriteChannel)
		snippetsMenu.addAction(self.cmdWriteChannel)

		self.cmdWriteUser = QAction("Write to user window",self)
		self.cmdWriteUser.triggered.connect(self.injectWriteUser)
		snippetsMenu.addAction(self.cmdWriteUser)

		self.cmdNick = QAction("Write to user window",self)
		self.cmdNick.triggered.connect(self.injectNick)
		snippetsMenu.addAction(self.cmdNick)

		self.cmdSleep = QAction("Sleep",self)
		self.cmdSleep.triggered.connect(self.injectSleep)
		snippetsMenu.addAction(self.cmdSleep)

		helpMenu = menubar.addMenu("Help")

		self.actHelp = QAction(QIcon(RESOURCE_ICON_HELP),"Commands",self)
		self.actHelp.triggered.connect(self.showDocs)
		helpMenu.addAction(self.actHelp)

		# self.actInject = QAction(QIcon(RESOURCE_IMAGE_RUN),"Run",self)
		# self.actInject.triggered.connect(self.inject)
		# scriptMenu.addAction(self.actInject)

		# edLayout = QVBoxLayout()
		# edLayout.addWidget(self.editor)
		# edLayout.addWidget(self.errors)
		# self.setLayout(edLayout)

		self.show()

	def showDocs(self):
		self.parent.showHTML(RESOURCE_COMMANDS_DOC_HTML,"QScript Commands")
		#self.parent.showHTML(RESOURCE_COMMANDS_DOC_HTML,"QScript Commands")
		#self.parent.showCMDDocs()
		# self.cmddocs = HTMLDialog.Dialog(parent=self)
		# self.cmddocs.openHTML(RESOURCE_COMMANDS_DOC_HTML,"QScript Commands")
		# self.cmddocs.show()

	def doFont(self):
		# self.editor.setFont(QFontDialog.getFont(0, self.editor.font()))
		# self.errors.setFont(self.editor.font())
		font, valid = QFontDialog.getFont(self.editor.font(),self)
		if valid:
			self.editor.setFont(font)
			self.errors.setFont(font)

	def injectSleep(self):
		self.editor.textCursor().insertText("# Change the number below to set sleep length, in seconds\nsleep 10")

	def injectNick(self):
		self.editor.textCursor().insertText("# Change NICKNAME to the desired nickname\nnick NICKNAME")

	def injectWriteUser(self):
		self.editor.textCursor().insertText("# Change NICKNAME to print text to the user's window\nwrite NICKNAME \"Text to print\"")

	def injectWriteChannel(self):
		self.editor.textCursor().insertText("# Change #CHANNEL to print text to the channel's window\nwrite #CHANNEL \"Text to print\"")

	def injectWriteServer(self):
		self.editor.textCursor().insertText("# This will print text in the server window\nwrite server \"Text to print\"")

	def injectWriteConsole(self):
		self.editor.textCursor().insertText("# This will print text to the console\nwrite console \"Text to print\"")

	def injectPart(self):
		self.editor.textCursor().insertText("# Change #CHANNEL to the name of the channel to part\npart #CHANNEL")

	def injectJoinKey(self):
		self.editor.textCursor().insertText("# Change #CHANNEL to the name of the channel to join\njoin #CHANNEL \"KEY\"")

	def injectJoin(self):
		self.editor.textCursor().insertText("# Change #CHANNEL to the name of the channel to join\njoin #CHANNEL")

	def XXXresizeEvent(self,resizeEvent):

		window_width = self.width()
		window_height = self.height()

		er_height = 75
		ed_height = window_height - er_height - 20
		

		self.editor.setGeometry(QtCore.QRect(0, 20, window_width, ed_height))
		self.errors.setGeometry(QtCore.QRect(0, ed_height+20, window_width, er_height))


class Highlighter(QSyntaxHighlighter):
	def __init__(self, parent=None):
		super(Highlighter, self).__init__(parent)

		keywordFormat = QTextCharFormat()
		keywordFormat.setForeground(Qt.darkBlue)
		keywordFormat.setFontWeight(QFont.Bold)

		# keywordPatterns = ["\\bchar\\b", "\\bclass\\b", "\\bconst\\b",
		# 		"\\bdouble\\b", "\\benum\\b", "\\bexplicit\\b", "\\bfriend\\b",
		# 		"\\binline\\b", "\\bint\\b", "\\blong\\b", "\\bnamespace\\b",
		# 		"\\boperator\\b", "\\bprivate\\b", "\\bprotected\\b",
		# 		"\\bpublic\\b", "\\bshort\\b", "\\bsignals\\b", "\\bsigned\\b",
		# 		"\\bslots\\b", "\\bstatic\\b", "\\bstruct\\b",
		# 		"\\btemplate\\b", "\\btypedef\\b", "\\btypename\\b",
		# 		"\\bunion\\b", "\\bunsigned\\b", "\\bvirtual\\b", "\\bvoid\\b",
		# 		"\\bvolatile\\b"]

		keywordPatterns = ["\\bjoin\\b", "\\bpart\\b", "\\bsleep\\b", "\\bmsleep\\b",
				"\\bactive\\b", "\\bnick\\b", "\\bwrite\\b", "\\bmsg\\b"]

		self.highlightingRules = [(QRegExp(pattern), keywordFormat)
				for pattern in keywordPatterns]



		targetFormat = QTextCharFormat()
		targetFormat.setForeground(Qt.magenta)
		targetFormat.setFontWeight(QFont.Bold)

		self.highlightingRules.append((QRegExp("\\bconsole\\b"), targetFormat))
		self.highlightingRules.append((QRegExp("\\bserver\\b"), targetFormat))

		# $variables
		varFormat = QTextCharFormat()
		varFormat.setForeground(Qt.blue)
		varFormat.setFontWeight(QFont.Bold)
		self.highlightingRules.append((QRegExp("\\B\\$\\w*\\b"), varFormat))

		# classFormat = QTextCharFormat()
		# classFormat.setFontWeight(QFont.Bold)
		# classFormat.setForeground(Qt.darkMagenta)
		# self.highlightingRules.append((QRegExp("\\bQ[A-Za-z]+\\b"),
		# 		classFormat))

		# singleLineCommentFormat = QTextCharFormat()
		# singleLineCommentFormat.setForeground(Qt.red)
		# self.highlightingRules.append((QRegExp("#[^\n]*"),
		# 		singleLineCommentFormat))

		singleLineCommentFormat = QTextCharFormat()
		singleLineCommentFormat.setForeground(Qt.red)
		self.highlightingRules.append((QRegExp("^#.*$"),
				singleLineCommentFormat))

		singleLineCommentFormat2 = QTextCharFormat()
		singleLineCommentFormat2.setForeground(Qt.red)
		self.highlightingRules.append((QRegExp("^\\s+#.*$"),
				singleLineCommentFormat2))

		# self.multiLineCommentFormat = QTextCharFormat()
		# self.multiLineCommentFormat.setForeground(Qt.red)

		quotationFormat = QTextCharFormat()
		quotationFormat.setForeground(Qt.darkGreen)
		self.highlightingRules.append((QRegExp("\".*\""), quotationFormat))


		channelFormat = QTextCharFormat()
		channelFormat.setFontWeight(QFont.Bold)
		channelFormat.setForeground(Qt.magenta)
		#self.highlightingRules.append((QRegExp("\\B#\\w+"), channelFormat))
		self.highlightingRules.append((QRegExp("\\B#\\w*\\b"), channelFormat))

		channelFormat2 = QTextCharFormat()
		channelFormat2.setFontWeight(QFont.Bold)
		channelFormat2.setForeground(Qt.magenta)
		#self.highlightingRules.append((QRegExp("\\B&\\w+"), channelFormat2))
		self.highlightingRules.append((QRegExp("\\B&\\w*\\b"), channelFormat))


		# functionFormat = QTextCharFormat()
		# functionFormat.setFontItalic(True)
		# functionFormat.setForeground(Qt.blue)
		# self.highlightingRules.append((QRegExp("\\b[A-Za-z0-9_]+(?=\\()"),
		# 		functionFormat))

		# self.commentStartExpression = QRegExp("/\\*")
		# self.commentEndExpression = QRegExp("\\*/")

	def highlightBlock(self, text):
		for pattern, format in self.highlightingRules:
			expression = QRegExp(pattern)
			index = expression.indexIn(text)
			while index >= 0:
				length = expression.matchedLength()
				self.setFormat(index, length, format)
				index = expression.indexIn(text, index + length)

		self.setCurrentBlockState(0)

		# startIndex = 0
		# if self.previousBlockState() != 1:
		# 	startIndex = self.commentStartExpression.indexIn(text)

		# while startIndex >= 0:
		# 	endIndex = self.commentEndExpression.indexIn(text, startIndex)

		# 	if endIndex == -1:
		# 		self.setCurrentBlockState(1)
		# 		commentLength = len(text) - startIndex
		# 	else:
		# 		commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()

		# 	self.setFormat(startIndex, commentLength,
		# 			self.multiLineCommentFormat)
		# 	startIndex = self.commentStartExpression.indexIn(text,
		# 			startIndex + commentLength);