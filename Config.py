from cryptography.fernet import Fernet
import configparser
import json
import os



TKN = "pvncnjdnkqxsk"
KY  = "knziiencnzjcn"

def encryptToken(token, key):
    f = Fernet(key)
    encryptedToken = f.encrypt(token.encode())
    return encryptedToken

def decryptToken(encryptedToken, key):
    f = Fernet(key)
    decryptedToken = f.decrypt(encryptedToken).decode()
    return decryptedToken


def generateKey():
    key = Fernet.generate_key()
    return key

def saveToken(token):
    key = generateKey()
    encryptedToken = encryptToken(token, key)
    config = configparser.ConfigParser()
    config.read('config.ini')
    defaultValues = config.defaults()
    defaultValues[TKN] = encryptedToken.decode()
    defaultValues[KY]  = key.decode()


    with open('config.ini', 'w') as configFile:
        config.write(configFile)

def loadToken():
    config = configparser.ConfigParser()
    config.read('config.ini')

    encryptedToken = config['DEFAULT'].get(TKN)
    key = config['DEFAULT'].get(KY)
   
    if not encryptedToken or not key:
        return ""
    decryptedToken = decryptToken(encryptedToken.encode(), key.encode())

    return decryptedToken

def deleteToken():
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config['DEFAULT'].get(TKN)
    key= config['DEFAULT'].get(KY)
    if token:
        config['DEFAULT'].pop(TKN)
    if key:
        config['DEFAULT'].pop(KY)
    with open('config.ini', 'w') as configFile:
        config.write(configFile)
    


def saveCommandList(commands):
    with open("BotDatas.json", "w") as f:
        json.dump(commands, f)

def loadCommandList():
    defaultDatas ={
                "master": {},
                "bot commands": [],
                "ban words"   : [],
                "bot admins"  : [], 
                }
    if os.path.exists('BotDatas.json'):
        with open("BotDatas.json", "r") as f:
            try:
                commands = json.load(f)
                return commands
            except Exception as e:
                
                return defaultDatas
    else: return defaultDatas

def isSaveTokenEnabled():
    config = configparser.ConfigParser()
    config.read('config.ini')
    isEnable = config['DEFAULT'].get("save token")
    if isEnable == None:
        toggleEnableSave(True) 
        return True
    return json.loads(isEnable)


def toggleEnableSave(value):
    config = configparser.ConfigParser()
    config.read('config.ini')
    defaultValues = config.defaults()
    defaultValues['save token'] = json.dumps(value)
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

def savePath(path):
    if os.path.isdir(path):
        newPath = path
    else:
        newPath = os.path.dirname(path)

    config = configparser.ConfigParser()
    config.read('config.ini')
    defaultValues = config.defaults()
    defaultValues['path'] = newPath
    with open('config.ini', 'w') as configFile:
        config.write(configFile)
    

def loadPath():
    config = configparser.ConfigParser()
    config.read('config.ini')
    path = config['DEFAULT'].get("path")
    if path:
        return path
    else: return "/"