import requests
import json




class TelegramBot():
    def __init__(self, botToken="", **kw):
        self.botToken = botToken
        self.errorHandler = kw.get('errorHandler')
        self.botDatas = kw.get("botDatas")
        self.serverCooldown = 2 if not kw.get("serverCooldown") else kw.get("serverCooldown")
        self.apiUrl = "https://api.telegram.org/bot"
        self.serverRunning = False

    def getMe(self, **kw):
        if kw.get("token"):
            res = json.loads(requests.post(f"{self.apiUrl+kw.get('token')}/getMe", timeout=5).content)
            return res
        res = json.loads(requests.post(f"{self.apiUrl+self.botToken}/getMe").content)
        return res