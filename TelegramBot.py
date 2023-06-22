import requests
import json


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
    
    def handleError(self, text, **kw):
        pass