import inspect
import yaml
import time

class Parser: 
    def __init__(self, bot):
        self.commandhand = CommandHandler(bot)
        self.bot = bot
    def parse(self,message):
        user = message[:message.find("PRIVMSG")].replace(" ","")
        channel = message[message.find("PRIVMSG")+len("PRIVMSG"):message.find(":",1)].replace(" ","")
        if (not "#" in channel):
            channel = user[user.find(":")+1:user.find("!")].strip()
        text = message[message.find(":",1)+1:]
        if(text.startswith(self.bot.prefix)):
            command = text[text.find(self.bot.prefix)+len(self.bot.prefix):].split()[0]
            text = text[text.find(self.bot.prefix)+len(self.bot.prefix)+len(command)+1:]
            self.commandhand.handle(user,channel,text,command)
            
class CommandHandler:
	def __init__(self, bot):
		self.bot = bot
	def handle(self, user, channel, args, command):
		nickn = user[user.find(":")+1:user.find("!")].strip()
		if(not command in self.bot.data["commands"]):
			self.bot.send("NOTICE "+nickn+" :Unknown command: "+command)
			return False
		hostn = user[user.find("@")+1:].strip()
		if not hostn in self.bot.data["userdata"].keys():
		    self.bot.data["userdata"][hostn] = {}
		usern = user[user.find("@")+1:].strip()
		perm = False	
		syntax = True
		if( "permission" in self.bot.data["commands"][command].keys()):
			commandPerm = self.bot.data["commands"][command]["permission"]
		else:
			if("category" in self.bot.data["commands"][command].keys()):
				commandPerm = self.bot.data["commands"][command]["category"]+"."+command
			else:
				perm = True
		if not perm:
			perm = self.permCheck(hostn,commandPerm)
		if("syntax" in self.bot.data["commands"][command].keys()):
			syntax = self.syntaxCheck(self.bot.data["commands"][command]["syntax"],args)
		if( "run" in self.bot.data["commands"][command] and perm):
			try:
				exec(self.bot.data["commands"][command]["run"])
			except Exception as e:
				print(e)
				self.bot.send("PRIVMSG "+channel+" :The command errored")
		elif (not perm):
			self.bot.send("NOTICE "+nickn+" :You do not have the required permission node, the command requires node: " + str(commandPerm))
		elif (not syntax):
			self.bot.send("NOTICE "+nickn+" :You do not have the required permission node, the command requires node: " + str(commandPerm))
		else:
			self.bot.send("PRIVMSG "+channel+" :This command does not have 'run' node, it cannot be executed.")
	def permCheck(self, userHost, cmdPerm):
		if not "permissions" in self.bot.data["userdata"][userHost]:
			self.bot.data["userdata"][userHost]["permissions"] = []
		for perm in self.bot.data["userdata"][userHost]["permissions"]:
			if "-" in perm:
				perm = perm.replace("-","")
				if perm == cmdPerm:
					return False
				elif ".*" in perm:
					if perm[:perm.find("*")-1] == cmdPerm[:cmdPerm.find(".")]:
						return False
				elif perm == "*":
					return False
			if perm == cmdPerm:
				return True
			elif ".*" in perm:
				if perm[:perm.find("*")-1] == cmdPerm[:cmdPerm.find(".")]:
					return True
			elif perm == "*":
				return True
		for perm in self.bot.data["variables"]["default-permission-nodes"]:
			if perm in cmdPerm:
				return True
	def syntaxCheck(self, syntaxStr,args):
		args = args.split()
		if("%" in syntaxStr):
			preSyntax = syntaxStr.split("%")
			for syntax in preSyntax:
				syntax = syntax.split()
				if(len(syntax) == len(args)):
					break
		else:
			syntax = syntaxStr.split()
		
				
