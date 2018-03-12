import socket
import sys
import time
import parser
import inspect
import os
import yaml
import json
import threading
import positron
from collections import defaultdict

positron.main_level = positron.LogLevel.DEBUG

class Bot:
    def __init__(self):
        self.configFile = "Config.yaml"
        
        with open(self.configFile, 'r') as stream:
            try:
                self.config = self.Struct(**yaml.load(stream))
            except Exception as exc:
                print(exc)

        self.data = {}
        
        self.channels = self.config.variables["channels"]
        self.server = self.config.variables["server"]
        self.botnick = self.config.variables["nickname"]
        self.prefix = self.config.variables["prefix"]
        password = self.config.secrets["password"]
        self.realname = self.config.variables["realname"]
        
        for d in self.config.variables["autoload"]:
            print(d)
            self.loadyaml(d)
            print(str(self.data))

        self.config.secrets = {}        

        self.log = positron.Logger()
        #self.log.enable_file_logging()
        self.log.iochars = "IRC"
        self.log.info("Hello, IRC!")

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.irc.connect((self.server, 6667))
        self.send("USER "+ self.botnick +" 0 * :"+self.realname)
        self.send("NICK "+ self.botnick)
        time.sleep(3)
        self.send("PRIVMSG NickServ :identify "+ password)
        time.sleep(3)
        for channel in self.channels:
            self.send("JOIN "+ channel)
    def send(self,msg):
        self.log.io("[RAW] " + msg)
        self.irc.send((msg + '\r\n').encode("utf-8"))
    def sendPrivmsg(self,reciever,msg):
        self.log.io("[PRIVMSG] " + msg)
        self.irc.send(("PRIVMSG "+reciever+" :"+ msg + '\r\n').encode("utf-8"))
    def sendNotice(self,nick,msg):
        self.log.io("[NOTICE] "+nick+ ": " + msg)
        self.irc.send(("NOTICE "+nick+" :"+ msg + '\r\n').encode("utf-8"))
    def recv(self):
        msg = self.irc.makefile().readline()[0:-1]
        self.log.io("[READ] " + msg)
        return msg
    class Struct:
        def __init__(self, **entries): 
            self.__dict__.update(entries)
    def loadyaml(self,yamlFile):
        try:
            if(not os.path.isfile(yamlFile)): return 1
            else:
                with open(yamlFile, 'r') as stream:
                    self.yaml = self.Struct(**yaml.load(stream))
                    for c in self.yaml.info["load"]:
                        if str(self.data) == "{}":
                            self.data = self.yaml.data
                        else:
                            self.data[c].update(self.yaml.data[c])
                    if self.yaml.info["run"]:
                        if ("onLoad") in self.yaml.info["run"]:
                            exec(self.yaml.data[self.yaml.info["run"].replace("onLoad:")])
                    return 0
        except Exception as e:
            print(e)
            return 2
    def dsum(*dicts):
        ret = defaultdict(int)
        for d in dicts:
            for k, v in d.items():
                ret[k] += v
        return dict(ret)

if __name__ == "__main__":
    bot = Bot()
    parser = parser.Parser(bot)
    while 1: 
        text=bot.recv()
        if text.find('PING') != -1:
            bot.send('PONG ' + text.split() [1])
        elif (text.find("PRIVMSG") != -1):
            try:
                parser.parse(text)
            except Exception as e:
                bot.log.error("error at parser")
                bot.log.error(str(e))
            
