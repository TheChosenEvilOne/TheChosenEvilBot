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
        text = message[message.find(":",1)+1:]
        if(text.startswith(self.bot.prefix)):
            command = text[text.find(self.bot.prefix)+len(self.bot.prefix):].split()[0]
            text = text[text.find(self.bot.prefix)+len(self.bot.prefix)+len(command)+1:]
            if(command in self.bot.data["commands"]):
                self.commandhand.handle(user,channel,text,command)
            else:
                self.bot.send("PRIVMSG "+channel+" :Unknown command: "+command)
            
class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
    def handle(self, user, channel, args, command):
        try:
            if (self.bot.data["variables"]["userdata"][user[user.find("@")+1:].strip()]["permission"] >= 0):
                perm = self.bot.data["variables"]["userdata"][user[user.find("@")+1:].strip()]["permission"]
        except Exception as e:
            print(e)
            self.bot.data["variables"]["userdata"][user[user.find("@")+1:]] = {}
            self.bot.data["variables"]["userdata"][user[user.find("@")+1:]]["permission"] = 0
            perm = 0
        if( "permission" in self.bot.data["commands"][command].keys()):
            commandPerm = self.bot.data["commands"][command]["permission"]
        else:
            commandPerm = 0
        if( "run" in self.bot.data["commands"][command] and perm >= commandPerm ):
            try:
                exec(self.bot.data["commands"][command]["run"])
            except Exception as e:
                print(e)
                self.bot.send("PRIVMSG "+channel+" :The command errored")
        elif (perm < commandPerm):
            self.bot.send("PRIVMSG "+channel+" :Your permission is too low (your current permission level is "+str(perm)+", the command requires " + str(commandPerm)+")")
