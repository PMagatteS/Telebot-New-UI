import requests
import json
import time
import datetime
from Config import loadCommandList, loadToken


def getTimestamp(text):
    currentTime = datetime.datetime.now()
    limits = {
        "Hour": currentTime + datetime.timedelta(hours=1),
        "Day": currentTime + datetime.timedelta(days=1),
        "Week": currentTime + datetime.timedelta(weeks=1),
        "Month": currentTime + datetime.timedelta(days=31),
        "Permanent": currentTime + datetime.timedelta(seconds=20),
    }

    limitTime = limits[text]
    timestamp = int(time.mktime(limitTime.timetuple()))
    return timestamp

def checkNetwork(func):
    def wrapper(*args, **kwargs):
        try:
            res= func(args[0], **kwargs)
            return res
        except Exception as err:
            args[0].handleError("Check your network connection")
            return "error"

class TelegramBot():
    def __init__(self, botToken="", **kw):
        self.botToken = botToken
        self.errorHandler = kw.get('errorHandler')
        self.botDatas = kw.get("botDatas")
        self.serverCooldown = 2 if not kw.get("serverCooldown") else kw.get("serverCooldown")
        self.apiUrl = "https://api.telegram.org/bot"
        self.serverRunning = False

    @checkNetwork
    def getMe(self, **kw):
        if kw.get("token"):
            res = json.loads(requests.post(f"{self.apiUrl+kw.get('token')}/getMe", timeout=5).content)
            return res
        res = json.loads(requests.post(f"{self.apiUrl+self.botToken}/getMe").content)
        return res
    
    @checkNetwork
    def getUpdate(self, **kw):
        if not kw.get("offset"):
            res = json.loads(requests.post(f"{self.apiUrl+self.botToken}/getUpdates", timeout=5).content)
        else:
            res = json.loads(requests.post(f"{self.apiUrl+self.botToken}/getUpdates", params={"offset": kw.get("offset")}, timeout=5).content)
        return res
    
    @checkNetwork
    def sendMessage(self, **kw):
        requests.post(f"{self.apiUrl+self.botToken}/sendMessage", params={
            "chat_id": kw.get("chatId"),
            "text": kw.get("text")
        })

    @checkNetwork
    def sendFile(self, **kw):
        res=requests.post(f"{self.apiUrl+self.botToken}/sendDocument" , timeout=5, params={
            "chat_id": kw.get("chatId"),
            "caption": kw.get("text"),
            "document": kw.get("fileId")
        })

    @checkNetwork
    def sendPhoto(self, **kw):
        res=requests.post(f"{self.apiUrl+self.botToken}/sendPhoto" , timeout=5, params={
            "chat_id": kw.get("chatId"),
            "caption": kw.get("text"),
            "photo": kw.get("fileId")
        })

    @checkNetwork
    def sendMediaGroup(self, **kw):
        res=requests.post(f"{self.apiUrl+self.botToken}/sendMediaGroup" , timeout=5, params={
            "chat_id": kw.get("chatId"),
            "media": json.dumps(kw.get("media"))
        })


    @checkNetwork
    def banChatMember(self, **kw):
        res=requests.post(f"{self.apiUrl+self.botToken}/banChatMember" , timeout=5, params={
            "chat_id": kw.get("chatId"),
            "user_id": kw.get("user"),
            "until_date": kw.get("date")
        })

    def getFileId(self, **kw):
        types = ["video", "document", "audio", "voice", "animation"]
        update = kw.get('update')
        if update.get("photo"):
                self.sendPhoto(
                    chatId= update.get("chat").get("id"),
                    text= f"Photo id : {update.get('photo')[0].get('file_id')}",
                    fileId= update.get('photo')[0].get('file_id')
                              )
                return

        for media in types:
            if update.get(media):
                self.sendFile(
                    chatId= update.get("chat").get("id"),
                    text= f"{media.capitalize()} id : {update.get(media).get('file_id')}",
                    fileId= update.get(media).get('file_id')
                              )
    
    def handleUpdates(self, **kw):
        updates = kw.get("updates")
        if not updates:
            updates = self.getUpdate().get("result")   

        for update in updates:
            if update.get("message"):
                message = update.get("message")

            elif update.get("edited_message"):
                message = update.get("edited_message")

            else: 
                continue

            if message.get("text"):
                text = message.get("text")
            elif message.get("caption"):
                text = message.get("caption")
            else:
                text = ""
            userName = message.get("from").get("username")
            self.isAdmin(name=userName, update=update, text=text) 
        return        
                
    def isAdmin(self, **kw):
        update, name, text= kw.get("update"), kw.get('name'), kw.get('text')
        offset = update.get("update_id")
        admins = self.botDatas.get("bot admins")
        adminList = [admin.get("name") for admin in admins]
        if name in adminList:
            for admin in admins:
                if name == admin.get("name"):
                    if "/get_all_ids" in text:
                        admin["getAllId"] = not admin.get("getAllId")

                    if admin.get("getAllId")  or "/get_file_id" in text:
                        if update.get("message"):
                            self.getFileId(update= update.get("message"))
                        elif update.get("edited_message"):
                            self.getFileId(update= update.get("edited_message"))
                    if self.isMaster(name=name):
                        if "/stop_bot_server" in text:
                            self.serverRunning = False
                    self.isBotCommand(text=text, update=update)
                else:
                    continue
        else:
            self.isBan(update= update, text=text)

        self.getUpdate(offset=offset+1)
    
    def isMaster(self, name, **kw):
        master = self.botDatas.get("master").get("name")
        if not master:
            return False
        if name == master:
            return True
        else:   
            return False

    def isBan(self, **kw):
        update,  text= kw.get("update"), kw.get('text')
        if not text:
            return
        banWords = self.botDatas.get("ban words")
        for word in banWords:

            if word.get("word") in text:
                self.banChatMember(chatId=update.get("message").get("chat").get("id"), 
                                   user= update.get("message").get("from").get("id"), 
                                   date=getTimestamp(word.get("time"))
                                   )
                return
            
        self.isBotCommand(update=update, text=text)

                
    def isBotCommand(self, **kw):
        update,  text= kw.get("update"), kw.get('text')
        message = update.get("message")
        commandList = self.botDatas.get("bot commands")
        typeOfCommands = {
            "Send message": self.sendMessage,
            "Send image": self.sendPhoto,
            "Send document": self.sendFile,
            "Send media group": self.sendMediaGroup
        }
        if not text:
            return
        for command in commandList:
            if command.get("name") in text:
                response = typeOfCommands.get(command.get("command type"))
                response(chatId=message.get("chat").get("id"), **command.get("args"))


    def handleError(self, text, **kw):
        if self.errorHandler:
            self.errorHandler(text)

    def runServer(self, **kw):
        isBot = self.getMe()
        if not isBot.get("ok"):
            print("Error: Couldn't Get Your Bot")
            return
        self.serverRunning = True
        while self.serverRunning:
            updates = self.getUpdate()
            result = updates.get("result")
            if len(result) > 0:
                self.handleUpdates(updates=result)
            time.sleep(self.serverCooldown)

if __name__ == "__main__":
    token = loadToken()
    botDatas = loadCommandList()
    bot = TelegramBot(botToken=token, botDatas=botDatas)
    bot.runServer()