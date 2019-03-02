

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

from PyQt5.QtCore import *

from quirc.common import *

from blinker import signal

import shlex
import time
import os

class QuircScriptThread(QThread):

	closewindow = pyqtSignal(str)
	channelmsg = pyqtSignal(list)
	errormsg = pyqtSignal(list)

	def __init__(self,client,gui,text,check):
		QThread.__init__(self)

		if os.path.isfile(text):
			f = open(text, "r")
			text = f.read()

		self.work = Script(client,gui,text,check)

	def got_close(self,sender,**kw):
		channel = kw['msg']
		self.closewindow.emit(channel)

	def got_cmsg(self,sender,**kw):
		msg = kw['msg']
		channel = kw['channel']
		self.channelmsg.emit([channel,msg])

	def got_error(self,sender,**kw):
		msg = kw['msg']
		line = kw['line']
		self.errormsg.emit([line,msg])

	def run(self):
		self.threadactive = True

		self.part_event = signal("closewindow")
		self.part_event.connect(self.got_close)

		self.chanmsg_event = signal("channelmessage")
		self.chanmsg_event.connect(self.got_cmsg)

		self.error_event = signal("errormsg")
		self.error_event.connect(self.got_error)

		self.work.exec()

	def stop(self):
		self.threadactive = False
		self.wait()

class Variable(object):

	def __init__(self,name,value):
		self.name = name
		self.value = value
		self.interp = f"{SCRIPT_VARIABLE_SYMBOL}{name}"

class Script(object):
	def __init__(self,client,gui,text,check):
		self.client = client
		self.gui = gui
		self.script = text
		self.errors = []
		self.check = check
		self.error_count = 0
		self.variables = []

	def addVariable(self,name,value):
		for v in self.variables:
			if v.name == name:
				err_event = signal("errormsg")
				err_event.send(self,line=line_number,msg=f"Variable {name} already exists")
				self.error_count = self.error_count + 1
				return
		v = Variable(name,value)
		self.variables.append(v)

	def setVariable(self,name,value):
		for v in self.variables:
			if v.name == name:
				v.value = value
				return
		err_event = signal("errormsg")
		err_event.send(self,line=line_number,msg=f"Variable {name} doesn't exist")
		self.error_count = self.error_count + 1

	def interpolateVariables(self,data):
		for v in self.variables:
			data = data.replace(v.interp,v.value)
		return data

	def exec(self):
		line_number = 0;
		for line in self.script.split("\n"):
			line.strip()
			if len(line)==0: continue
			tokens = shlex.split(line)
			line_number = line_number + 1

			if len(tokens) >= 1 and len(tokens[0]) >= 1:
				if tokens[0] == '#':
					continue

			if len(tokens) >= 1 and tokens[0] == "var":
				if len(tokens) == 3:
					tokens.pop(0)
					vname = tokens.pop(0)
					vcont = tokens.pop(0)
					vcont = self.interpolateVariables(vcont)
					self.addVariable(vname,vcont)
				else:
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"var\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "set":
				if len(tokens) == 3:
					tokens.pop(0)
					vname = tokens.pop(0)
					vcont = tokens.pop(0)
					vcont = self.interpolateVariables(vcont)
					self.setVariable(vname,vcont)
				else:
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"set\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "raw":
				if len(tokens) >= 3:
					tokens.pop(0)
					cmd = tokens.pop(0)
					cmd = self.interpolateVariables(cmd)
					nt = []
					for m in tokens:
						nt.append(self.interpolateVariables(m))
					tokens = nt
					if self.check == RUN_SCRIPT:
						self.client.send_items(cmd.upper(),*tokens)
				else:
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"raw\"")
					self.error_count = self.error_count + 1
				continue


			if len(tokens) >= 1 and tokens[0] == "write":
				if len(tokens) > 2:
					tokens.pop(0)
					channel = tokens.pop(0)
					txt = ' '.join(tokens)
					# interpolate variables
					channel = self.interpolateVariables(channel)
					txt = self.interpolateVariables(txt)
					if self.check == RUN_SCRIPT:
						chan_event = signal("channelmessage")
						chan_event.send(self,msg=txt,channel=channel)
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"write\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"write\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "join":
				if len(tokens) == 2:
					tokens.pop(0)
					chan = tokens[0]
					# interpolate variables
					chan = self.interpolateVariables(chan)
					if self.check == RUN_SCRIPT: self.client.join(chan)
				elif len(tokens) >= 3:
					tokens.pop(0)
					chan = tokens.pop(0)
					key = ' '.join(tokens)
					# interpolate variables
					chan = self.interpolateVariables(chan)
					key = self.interpolateVariables(key)
					if self.check == RUN_SCRIPT: self.client.join(chan,key)
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"join\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"join\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "part":
				if len(tokens) == 2:
					tokens.pop(0)
					chan = tokens[0]
					#if self.check == 0: self.client.part(chan)
					# interpolate variables
					chan = self.interpolateVariables(chan)
					if self.check == RUN_SCRIPT:
						#self.gui.partChannel(chan)
						part_event = signal("closewindow")
						part_event.send(self,msg=chan)
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"part\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"part\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "nick":
				if len(tokens) == 2:
					tokens.pop(0)
					newnick = tokens[0]
					# interpolate variables
					newnick = self.interpolateVariables(newnick)
					if self.check == RUN_SCRIPT:
						self.client.nick(newnick)
						self.gui.nickname = newnick
						self.gui.refresh_all_users()
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"nick\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"nick\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "sleep":
				if len(tokens) == 2:
					tokens.pop(0)
					nap = tokens[0]
					# interpolate variables
					nap = self.interpolateVariables(nap)
					if self.check == RUN_SCRIPT: time.sleep(int(nap))
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"sleep\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"sleep\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "msleep":
				if len(tokens) == 2:
					tokens.pop(0)
					nap = tokens[0]
					# interpolate variables
					nap = self.interpolateVariables(nap)
					if self.check == RUN_SCRIPT:
						time.sleep(int(nap)/1000.0)
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"sleep\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"sleep\"")
					self.error_count = self.error_count + 1
				continue

			if len(tokens) >= 1 and tokens[0] == "msg":
				if len(tokens) >= 3:
					tokens.pop(0)
					target = tokens.pop(0)
					# interpolate variables
					target = self.interpolateVariables(target)
					nt = []
					for m in tokens:
						nt.append(self.interpolateVariables(m))
					tokens = nt
					if self.check == RUN_SCRIPT:
						for m in tokens:
							self.client.privmsg(target,m)
				else:
					#self.errors.append(f"{line_number}: Not enough arguments to \"join\"")
					err_event = signal("errormsg")
					err_event.send(self,line=line_number,msg="Not enough arguments to \"msg\"")
					self.error_count = self.error_count + 1
				continue

			# not recognized
			err_event = signal("errormsg")
			err_event.send(self,line=line_number,msg=f"Unrecognized statement: {line}")
			self.error_count = self.error_count + 1

		if self.error_count > 0:
			err_event = signal("errormsg")
			err_event.send(self,line=str(0),msg=f"{self.error_count} error(s) found.")
		else:
			err_event = signal("errormsg")
			err_event.send(self,line=str(0),msg="No errors found.")








