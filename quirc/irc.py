
SSL_AVAILABLE = True

import sys
import datetime
from quirc.common import *

from twisted.internet import reactor, protocol

try:
	from twisted.internet import ssl
except ImportError as error:
	# Output expected ImportErrors.
	print(error.__class__.__name__ + ": " + error.message)
	SSL_AVAILABLE = False
except Exception as exception:
	# Output unexpected Exceptions.
	print(exception, False)
	print(exception.__class__.__name__ + ": " + exception.message)

from twisted.words.protocols import irc


#from jonesplugins import PluginCollection

	# def run(self):
	# 	if self.use_ssl:
	# 		bot = IRC_Connection_Factory(self.nickname,self.username, self.ircname)
	# 		reactor.connectSSL(self.server,self.port,bot,ssl.ClientContextFactory())
	# 		reactor.run(installSignalHandlers=0)
	# 	else:
	# 		bot = IRC_Connection_Factory(self.nickname,self.username, self.ircname)
	# 		reactor.connectTCP(self.server, self.port, bot)
	# 		reactor.run(installSignalHandlers=0)

def connect(host,port,nick,username=None,ircname=None,gui=None,password=None):
	bot = IRC_Connection_Factory(nick,username,ircname,gui,password)
	reactor.connectTCP(host,port,bot)
	#reactor.run(installSignalHandlers=0)

def connectSSL(host,port,nick,username=None,ircname=None,gui=None,password=None):
	bot = IRC_Connection_Factory(nick,username,ircname,gui,password)
	reactor.connectSSL(host,port,bot,ssl.ClientContextFactory())

client = None

# =====================================
# | TWISTED IRC CONNECTION MANAGEMENT |
# =====================================

class IRC_Connection(irc.IRCClient):
	nickname = 'bot'
	realname = 'bot'
	username = 'bot'

	def __init__(self,nickname,username,realname,gui,password):
		self.nickname = nickname
		self.username = username
		self.realname = realname
		if password != None:
			self.password = password
		self.gui = gui

		self.users = {}

		self.whois_data = {}

	def connectionMade(self):

		self.gui.connected()

		self.gui.setClient(self)

		irc.IRCClient.connectionMade(self)

	def connectionLost(self, reason):

		self.gui.disconnected()

		irc.IRCClient.connectionLost(self, reason)

	def signedOn(self):

		self.gui.setClient(self)

		self.gui.registered()

		self.join("#quirc")

	def joined(self, channel):
		self.gui.joinedChannel(channel)

	def privmsg(self, user, target, msg):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]

		tokens = msg.split(' ')

		if target==self.nickname:
			self.gui.privatemsg(user,msg)
		else:
			self.gui.publicmsg(user,target,msg)


	def noticed(self, user, channel, message):
		tok = user.split('!')
		if len(tok) >= 2:
			pnick = tok[0]
			phostmask = tok[1]
		else:
			pnick = user
			phostmask = user

		self.gui.notice(user,channel,message)

		

	def receivedMOTD(self, motd):

		self.gui.motd(motd)

	def modeChanged(self, user, channel, set, modes, args):
		p = user.split('!')
		if len(p) == 2:
			pnick = user.split('!')[0]
			phostmask = user.split('!')[1]
		else:
			pnick = user
			phostmask = user

		msg = []

		if 'o' in modes:
			self.sendLine(f"NAMES {channel}")
			if set:
				for u in args:
					msg.append(f"{pnick} gave {u} operator status")
			else:
				for u in args:
					msg.append(f"{pnick} removed operator status from {u}")
		if 'v' in modes:
			self.sendLine(f"NAMES {channel}")
			if set:
				for u in args:
					msg.append(f"{pnick} gave {u} voiced status")
			else:
				for u in args:
					msg.append(f"{pnick} removed voiced status from {u}")
		if 'p' in modes:
			if set:
				msg.append(f"{pnick} set channel status to private")
			else:
				msg.append(f"{pnick} set channel status to public")
		if 'k' in modes:
			if len(args) >= 1:
				nkey = args[0]
			else:
				nkey = ''
			if set:
				msg.append(f"{pnick} set channel key to '{nkey}'")
			else:
				msg.append(f"{pnick} removed channel key")

		if len(msg)>0:
			for m in msg:
				# modemsg(self,user,channel,txt)
				self.gui.modemsg(user,channel,m)
			return

		self.gui.mode(user,channel,set,modes,args)
		

	def userJoined(self, user, channel):
		if user.split('!')[0] == self.nickname:
			return
		self.sendLine(f"NAMES {channel}")
		self.gui.joined(user,channel)

	def userLeft(self, user, channel):
		self.sendLine(f"NAMES {channel}")
		self.gui.parted(user,channel)

	def irc_ERR_NICKNAMEINUSE(self, prefix, params):
		newnick = self.nickname + "_"
		self.setNick(newnick)
		self.gui.nickname = newnick
		self.gui.clientIsConnected()

		for w in self.gui.windows:
			if w == self.gui.server: continue
			self.sendLine(f"NAMES {w}")

	def userRenamed(self, oldname, newname):
		self.gui.rename(oldname,newname)

	def topicUpdated(self, user, channel, newTopic):
		self.gui.topic(user,channel,newTopic)

	def action(self, user, channel, data):
		pnick = user.split('!')[0]
		phostmask = user.split('!')[1]
		self.gui.action(user,channel,data)

	def userKicked(self, kickee, channel, kicker, message):
		self.sendLine(f"NAMES {channel}")
		self.gui.kick(kicker,kickee,channel,message)

	def kickedFrom(self, channel, kicker, message):
		self.gui.kicked(kicker,channel,message)

	def irc_QUIT(self,prefix,params):
		# fetch_userlist(self)
		x = prefix.split('!')
		if len(x) >= 2:
			nick = x[0]
		else:
			nick = prefix
		if len(params) >=1:
			m = params[0].split(':')
			if len(m)>=2:
				msg = m[1].strip()
			else:
				msg = ""
		else:
			msg = ""

		self.gui.quit(prefix,msg)

	def irc_RPL_NAMREPLY(self, prefix, params):
		channel = params[2].lower()
		nicklist = params[3].split(' ')

		if channel in self.users:
			for n in nicklist:
				if len(n)==0: continue
				if n.isspace(): continue
				self.users[channel].append(n)
		else:
			self.users[channel] = []
			for n in nicklist:
				if len(n)==0: continue
				if n.isspace(): continue
				self.users[channel].append(n)

	def irc_RPL_ENDOFNAMES(self, prefix, params):

		channel = params[1].lower()

		users = self.users[channel]
		del self.users[channel]

		ops = []
		voiced = []
		norm = []

		for u in users:
			if u[0]=='@':
				ops.append(u)
				continue
			if u[0]=='+':
				voiced.append(u)
				continue
			norm.append(u)

		users = ops + voiced + norm

		self.gui.users(channel,users)


	def irc_RPL_TOPIC(self, prefix, params):
		# global TOPIC
		if not params[2].isspace():
			TOPIC = params[2]
		else:
			TOPIC = ""

		channel = params[1]
		self.gui.topic(prefix,channel,TOPIC)

	def irc_RPL_WHOISCHANNELS(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		channels = ", ".join(params)

		if nick in self.whois_data:
			self.whois_data[nick].name = nick
			self.whois_data[nick].channels = params
		else:
			self.whois_data[nick] = Whois()
			self.whois_data[nick].name = nick
			self.whois_data[nick].channels = params

	def irc_RPL_WHOISUSER(self, prefix, params):
		nick = params[1]
		username = params[2]
		host = params[3]
		realname = params[5]

		if nick in self.whois_data:
			self.whois_data[nick].name = nick
			self.whois_data[nick].username = username
			self.whois_data[nick].host = host
			self.whois_data[nick].realname = realname
		else:
			self.whois_data[nick] = Whois()
			self.whois_data[nick].name = nick
			self.whois_data[nick].username = username
			self.whois_data[nick].host = host
			self.whois_data[nick].realname = realname

	def irc_RPL_WHOISIDLE(self, prefix, params):
		params.pop(0)
		nick = params.pop(0)
		idle_time = params.pop(0)
		signed_on = params.pop(0)

		if nick in self.whois_data:
			self.whois_data[nick].name = nick
			self.whois_data[nick].idle = idle_time
			self.whois_data[nick].signedon = signed_on
		else:
			self.whois_data[nick] = Whois()
			self.whois_data[nick].name = nick
			self.whois_data[nick].idle = idle_time
			self.whois_data[nick].signedon = signed_on

	def irc_RPL_WHOISSERVER(self, prefix, params):
		nick = params[1]
		server = params[2]

		if nick in self.whois_data:
			self.whois_data[nick].name = nick
			self.whois_data[nick].server = server
		else:
			self.whois_data[nick] = Whois()
			self.whois_data[nick].name = nick
			self.whois_data[nick].server = server

	def irc_RPL_ENDOFWHOIS(self, prefix, params):
		nick = params[1]

		if nick in self.whois_data:
			self.gui.whois(self.whois_data[nick])
			del self.whois_data[nick]

	def irc_RPL_WHOWASUSER(self, prefix, params):
		nick = params[1]
		username = params[2]
		host = params[3]
		realname = params[5]

	def irc_RPL_ENDOFWHOWAS(self, prefix, params):
		nick = params[1]

	def irc_RPL_WHOREPLY(self, prefix, params):
		channel = params[1]
		username = params[2]
		host = params[3]
		server = params[4]
		nick = params[5]
		hr = params[7].split(' ')

	def irc_RPL_ENDOFWHO(self, prefix, params):
		nick = params[1]
		#server_info_msg_display(ircform,"WHO",f"End of who data for {nick}")

	def irc_RPL_INVITING(self, prefix, params):
		channel = params[1]
		nick = params[2]
		#system_msg_display(ircform,f"Invitation to {channel} sent to {nick}")

	def irc_RPL_VERSION(self, prefix, params):
		sversion = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"VERSION",f"Server version: {sversion}")

	def irc_RPL_CHANNELMODEIS(self, prefix, params):
		channel = params[1]
		# if params[2] == '+' or params[2] == '-':
		# 	server_info_msg_display(ircform,"MODE",f"{channel} has no modes set")
		# 	return
		# modes = f"{params[2]} {params[3]}"
		# server_info_msg_display(ircform,"MODE",f"{channel} mode(s): {modes}")

	def irc_RPL_YOUREOPER(self, prefix, params):
		#system_msg_display(ircform,f"You are now an IRC operator")
		pass

	def irc_RPL_TIME(self, prefix, params):
		t = params[2]
		#server_info_msg_display(ircform,"TIME",f"Server time/date: {t}")

	def irc_RPL_INFO(self, prefix, params):
		#server_info_msg_display(ircform,"INFO",f"{params[1]}")
		pass

	def irc_RPL_ENDOFINFO(self, prefix, params):
		#server_info_msg_display(ircform,"INFO","End of info data")
		pass

	def irc_RPL_LIST(self, prefix, params):
		chan = params[1]
		crowd = params[2]
		topic = params[3]
		# if topic == ' ':
		# 	if int(crowd) > 1:
		# 		server_info_msg_display(ircform,"LIST",f"{chan} ({crowd} users)")
		# 	else:
		# 		server_info_msg_display(ircform,"LIST",f"{chan} (1 user)")
		# else:
		# 	topic = topic.strip()
		# 	if int(crowd) > 1:
		# 		server_info_msg_display(ircform,"LIST",f"{chan} ({crowd} users): \"{topic}\"")
		# 	else:
		# 		server_info_msg_display(ircform,"LIST",f"{chan} ({crowd} user): \"{topic}\"")

	def irc_RPL_LISTSTART(self, prefix, params):
		#server_info_msg_display(ircform,"LIST",f"Start of list data")
		pass

	def irc_RPL_LISTEND(self, prefix, params):
		#server_info_msg_display(ircform,"LIST",f"End of list data")
		pass

	def irc_RPL_LUSERCLIENT(self, prefix, params):
		msg = params[1]
		#server_info_msg_display(ircform,"LUSER",f"Clients: {msg}")

	def irc_RPL_LUSERME(self, prefix, params):
		msg = params[1]
		#server_info_msg_display(ircform,"LUSER",f"This server: {msg}")

	def irc_RPL_LUSEROP(self, prefix, params):
		msg = params[1]
		#server_info_msg_display(ircform,"LUSER",f"Ops: {msg}")

	def irc_RPL_LUSERCHANNELS(self, prefix, params):
		msg = params[1]
		#server_info_msg_display(ircform,"LUSER",f"Channels: {msg}")

	def irc_RPL_STATSLINKINFO(self, prefix, params):
		linkname = params[1]
		data_queue = params[2]
		sent_msg = params[3]
		sent_kb = params[4]
		recvd_msg = params[5]
		recvd_kb = params[6]
		link_time = params[7]
		#server_info_msg_display(ircform,"STATS",f"{linkname} link: {data_queue} queued data, {sent_msg} sent messages, {sent_kb} kilobytes sent, {recvd_msg} messages received, {recvd_kb} kilobytes received, connected for {link_time}")

	def irc_RPL_STATSCOMMANDS(self, prefix, params):
		cmd = params[1]
		count = params[2]
		nbytes = params[3]
		remote = params[4]
		#server_info_msg_display(ircform,"STATS",f"Commands \"{cmd}\": {count} use(s), bytes {nbytes}, remote count: {remote}")

	def irc_RPL_STATSUPTIME(self, prefix, params):
		#server_info_msg_display(ircform,"STATS",f"Uptime: {params[1]}")
		pass

	def irc_RPL_STATSOLINE(self, prefix, params):
		params.pop(0)
		#server_info_msg_display(ircform,"STATS",f"O-line hosts: {' '.join(params)}")

	def irc_RPL_ENDOFSTATS(self, prefix, params):
		#server_info_msg_display(ircform,"STATS",f"End stat info for {SERVER}")
		pass

	def irc_RPL_TRACELINK(self, prefix, params):
		vanddebug = params[1]
		dest = params[2]
		nexts = params[3]
		protocol = params[4]
		luptime = params[5]
		back_queue = params[6]
		up_queue = params[7]
		#server_info_msg_display(ircform,"TRACE",f"Link {vanddebug}, destination {dest}, next server {nexts}, protocol version {protocol}, link uptime {luptime}, backstream queue {back_queue}, upstream queue {up_queue}")

	def irc_RPL_TRACECONNECTING(self, prefix, params):
		sclass = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Connecting {server}, {sclass}")

	def irc_RPL_TRACEHANDSHAKE(self, prefix, params):
		sclass = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Handshake {server}, {sclass}")

	def irc_RPL_TRACEUNKNOWN(self, prefix, params):
		sclass = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Unknown {server}, {sclass}")

	def irc_RPL_TRACEOPERATOR(self, prefix, params):
		sclass = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Operator {server}, {sclass}")

	def irc_RPL_TRACEUSER(self, prefix, params):
		sclass = params[1]
		server = params[2]
		#server_info_msg_display(ircform,"TRACE",f"User {server}, {sclass}")

	def irc_RPL_TRACESERVER(self, prefix, params):
		sclass = params[1]
		server = params[4]
		nhm = params[5]
		protocol = params[6]
		#server_info_msg_display(ircform,"TRACE",f"Server {server}, {sclass}, {nhm}, protocol {protocol}")

	def irc_RPL_TRACESERVICE(self, prefix, params):
		sclass = params[1]
		name = params[2]
		ttype = params[3]
		atype = params[4]
		#server_info_msg_display(ircform,"TRACE",f"Service {sclass}, {name}, type {ttype}, active type {atype}")

	def irc_RPL_TRACENEWTYPE(self, prefix, params):
		sclass = params[1]
		name = params[2]
		#server_info_msg_display(ircform,"TRACE",f"New Type {sclass}, {name}")

	def irc_RPL_TRACECLASS(self, prefix, params):
		sclass = params[1]
		ccount = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Class {sclass}, {ccount}")

	def irc_RPL_TRACELOG(self, prefix, params):
		logfile = params[1]
		debugl = params[2]
		#server_info_msg_display(ircform,"TRACE",f"Log {logfile}, {debugl}")

	def irc_RPL_TRACEEND(self, prefix, params):
		server = params[1]
		vers = params[2]
		#server_info_msg_display(ircform,"TRACE",f"End of trace information for {server} {vers}")

	def irc_RPL_ADMINME(self,prefix,params):
		#server_info_msg_display(ircform,"ADMIN",f"{params[1]}")
		pass

	def irc_RPL_ADMINLOC1(self,prefix,params):
		#server_info_msg_display(ircform,"ADMIN",f"{params[1]}")
		pass

	def irc_RPL_ADMINLOC2(self,prefix,params):
		#server_info_msg_display(ircform,"ADMIN",f"{params[1]}")
		pass

	def irc_RPL_ADMINEMAIL(self,prefix,params):
		#server_info_msg_display(ircform,"ADMIN",f"{params[1]}")
		pass

	def lineReceived(self, line):
		try:
			line2 = line.decode("UTF-8")
		except UnicodeDecodeError:
			line2 = line.decode("CP1252", 'replace')
		d = line2.split(" ")
		if len(d) >= 2:
			if d[1].isalpha(): return irc.IRCClient.lineReceived(self, line)
		if "Cannot join channel (+k)" in line2:
			self.gui.ircerror(f"Cannot join channel (wrong or missing password)")
		if "Cannot join channel (+l)" in line2:
			self.gui.ircerror(f"Cannot join channel (channel is full)")
		if "Cannot join channel (+b)" in line2:
			self.gui.ircerror(f"Cannot join channel (banned)")
		if "Cannot join channel (+i)" in line2:
			self.gui.ircerror(f"Cannot join channel (channel is invite only)")
		if "not an IRC operator" in line2:
			self.gui.ircerror("Permission denied (you're not an IRC operator")
		if "not channel operator" in line2:
			self.gui.ircerror("Permission denied (you're not channel operator)")
		if "is already on channel" in line2:
			self.gui.ircerror("Invite failed (user is already in channel)")
		if "not on that channel" in line2:
			self.gui.ircerror("Permission denied (you're not in channel)")
		if "aren't on that channel" in line2:
			self.gui.ircerror("Permission denied (target user is not in channel)")
		if "have not registered" in line2:
			self.gui.ircerror("You're not registered")
		if "may not reregister" in line2:
			self.gui.ircerror("You can't reregister")
		if "enough parameters" in line2:
			self.gui.ircerror("Error: not enough parameters supplied to command")
		if "isn't among the privileged" in line2:
			self.gui.ircerror("Registration refused (server isn't setup to allow connections from your host)")
		if "Password incorrect" in line2:
			self.gui.ircerror("Permission denied (incorrect password)")
		if "banned from this server" in line2:
			self.gui.ircerror("You are banned from this server")
		if "kill a server" in line2:
			self.gui.ircerror("Permission denied (you can't kill a server)")
		if "O-lines for your host" in line2:
			self.gui.ircerror("Error: no O-lines for your host")
		if "Unknown MODE flag" in line2:
			self.gui.ircerror("Error: unknown MODE flag")
		if "change mode for other users" in line2:
			self.gui.ircerror("Permission denied (can't change mode for other users)")
		return irc.IRCClient.lineReceived(self, line)

class IRC_Connection_Factory(protocol.ClientFactory):
	def __init__(self,nickname,username,realname,gui,password):
		self.nickname = nickname
		self.username = username
		self.realname = realname
		self.gui = gui
		self.password = password

	def buildProtocol(self, addr):
		bot = IRC_Connection(self.nickname,self.username,self.realname,self.gui,self.password)
		bot.factory = self
		return bot

	def clientConnectionLost(self, connector, reason):
		pass

	def clientConnectionFailed(self, connector, reason):
		pass
