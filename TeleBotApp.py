from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawer, MDNavigationDrawerHeader
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivymd.uix.dialog import MDDialog
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.scrollview import MDScrollView
from kivy.clock import Clock
from kivy.metrics import dp

import threading
import os
import json
import shutil

from TelegramBot import TelegramBot
from Config import saveCommandList, loadCommandList, saveToken, loadToken, toggleEnableSave, isSaveTokenEnabled, deleteToken, savePath, loadPath
from Help import helps
# The main commands of the bots
BotCommands = ["Send Message", "Send Image", "Send Video", "Send File", "Send Audio", "Media Group"]
# Will add more screen to those lists
largeScreens = ["Command List", "Handle Media Group"]
longScreens  = [*BotCommands, "Help", "Token"]
# Choice user will have for bans
BanTimes = ["Hour", "Day", "Week", "Month", "Permanent"]
# For the command's datatable
MediaTypes = ["Send File", "Send Image", "Send Video", "Send Audio"]
# Columns for datatables
commandListCols = [("N.", dp(20)), ("Command Type", dp(40)), ("Command Name", dp(40)), ("Media Id", dp(30)), ("Caption", dp(60)),]
mediaGroupCols = [ ("N.", dp(20)), ("Type", dp(50)), ("Caption", dp(50)),  ("Media Id", dp(50)),]
bannedWordsCols = [ ("N.", dp(20)), ("Word", dp(40)), ("Time", dp(40))]
adminListCols = [ ("N.", dp(20)), ("Name", dp(40)), ("Status", dp(40))]
# Items for dropdown in the dashboard
DropdownBotItems = [ { "viewclass": "OneLineListItem", "text": "Load Datas", "height": 56, "on_release": lambda: App.get_running_app().root.loadFile(), }, { "viewclass": "OneLineListItem", "text": "Save Datas", "height": 56, "on_release": lambda: App.get_running_app().root.saveData(), }, { "viewclass": "OneLineListItem", "text": "Get Server File", "height": 56, "on_release": lambda: App.get_running_app().root.getServerFiles(), }, ]
# Function to close the dropdown otherwise it stay dislplayed
def closeFilesDropdown():
       App.get_running_app().root.children[1].dashboard.fileDropdown.dismiss()
       
def startBot():
       App.get_running_app().root.startBot()
       

def stopBot():
       App.get_running_app().root.stopBot()

def saveDatas():
       datas = App.get_running_app().root.BotDatas
       saveCommandList(datas)

def refreshBanWords():
       App.get_running_app().root.children[1].bannedWords.mapData()

def refreshDataTable():
       App.get_running_app().root.children[1].dataTable.mapData()

def refreashMediaGroup():
       App.get_running_app().root.children[1].handleMediaGroup.mapData()

def refreshAdmins():
       App.get_running_app().root.children[1].adminList.mapData()

def infoDialog(text, title=""):
       dialog = MDDialog( title=title, text=text, buttons=[MDRaisedButton(text="DISCARD", on_press= lambda x: dialog.dismiss()),], )
       dialog.open()

def changeHeader(title=None, text=None):
       header = App.get_running_app().root.children[0].drawerHeader
       if title:
              header.title = title
       if text: 
              header.text = text

def toggleDrawer(*args):
       App.get_running_app().root.children[0].set_state("toggle")

def changeScreen(name):
    drawer = App.get_running_app().root.children[0]
    if drawer.state == "open":
            toggleDrawer()

    manager = App.get_running_app().root.children[1]
    try:
            manager.get_screen(name)
    except:
            return
    if name in longScreens:
            Window.size = (450, 600)
    if name in largeScreens:
            Window.size = (900, 400)
    manager.current = name  

class MainToolBar(MDTopAppBar):
       def __init__(self, **kwargs):
              super().__init__(**kwargs)
              self.left_action_items= [["menu", lambda x: toggleDrawer()]]
              self.pos_hint = {'top': 1}
              self.elevation = 0

# Send Message and child classes
class SendMessageScreen(Screen):
       def __init__(self, label, **kwargs):
              super(SendMessageScreen, self).__init__(**kwargs)
              self.toolbar = MainToolBar(title="Add Send Message Command")
              self.requieredCaption = True
              self.label = MDLabel(text=label, halign="center")
              self.commandName = MDTextField(hint_text="Enter command name", helper_text_mode="on_error", helper_text = "Requiered Field")
              self.message = MDTextField(hint_text="Enter message (multilines)",  helper_text_mode="on_error", multiline= True, size_hint_y= 1)
              self.box = GridLayout(cols=1, spacing=10, size_hint_y= None,pos_hint={'center_x': 0.5, 'top': .8}, size_hint_x= .8)
              self.validate = MDRaisedButton(text="Add command", pos_hint={'center_x': 0.5, 'top': 1}, on_press=self.addToCommandList)
              self.buttonBox = FloatLayout(size_hint_x= 1)
              self.messageBox = MDBoxLayout(size_hint=(.1, None))
              self.buttonBox.add_widget(self.validate)
              self.messageBox.add_widget(self.message)
              self.box.add_widget(self.label)
              self.box.add_widget(self.commandName)
              self.box.add_widget(self.messageBox)
              self.box.add_widget(self.buttonBox)
              self.add_widget(self.toolbar)
              self.add_widget(self.box)

       def addToCommandList(self, button):
              appDatas = App.get_running_app().root.BotDatas.get('bot commands')
              commandName = self.commandName.text
              caption = self.message.text
              
              self.commandName.error =  len(commandName) == 0
                     
              if len(caption) == 0 and self.requieredCaption:
                     self.message.helper_text = "Requiered Field"
                     self.message.error = True
              elif len(caption) > 1024 and not self.requieredCaption:
                     self.message.helper_text = f"Max length 1024 your current length {len(caption)}"
                     self.message.error = True

              elif len(caption) > 4096:
                     self.message.helper_text = f"Max length 4096 your current length {len(caption)}"
                     self.message.error = True
              else:
                     self.message.error = False
                     
              if "mediaID" in dir(self):
                     if len(self.mediaID.text) == 0:
                            self.mediaID.error = True
                            
              if len(commandName) > 0 and (len(caption)>0 and len(caption) <4097 and self.requieredCaption)or (not self.requieredCaption and len(self.mediaID.text) > 0 and len(caption) <1025):
                     if  self.requieredCaption:
                            appDatas.append({"name": commandName, "command type": "Send message", "displayed type": "Send Message", "args": {"text": caption}})
                            saveDatas()
                     else:  
                            if self.mediaType == "Image":
                                   appDatas.append({"name": commandName, "command type": "Send image", "displayed type": "Send Image", "args": {"caption": caption, "fileId":self.mediaID.text}})
                            else:
                                   appDatas.append({"name": commandName, "command type": "Send document", "displayed type": f"Send {self.mediaType}", "args": {"caption": caption, "fileId":self.mediaID.text}})
                            saveDatas()
                            self.mediaID.text = ""
                     self.commandName.text = ""
                     self.message.text = ""
                     refreshDataTable()
                     
              else: 
                     return
              
class SendFile(SendMessageScreen):
       def __init__(self, label, mediaType, **kwargs):
              super(SendFile, self).__init__(label, **kwargs)
              self.mediaType = mediaType
              self.IdBox = MDBoxLayout(size_hint=(.1, None), orientation= 'vertical')
              self.question_icon = MDIconButton(icon="help-circle", pos_hint={"top":1, "right": 1}, on_press= self.gotoMediaId)
              self.requieredCaption = False
              self.mediaID = MDTextField(hint_text=f"Enter {mediaType} id", helper_text_mode="on_error", helper_text = "Requiered Field", pos_hint={"center_y": .5}, size_hint=(1, None))
              self.toolbar.title = f"Add Send {mediaType} Command"
              self.IdBox.add_widget(self.question_icon)
              self.IdBox.add_widget(self.mediaID)
              self.box.add_widget(self.IdBox, 2)
              self.message.hint_text= "Caption(not requiered)"

       def gotoMediaId(self, button):
              changeScreen("Help")
              #TODO scroll to the right section

class SendMediaGroup(SendFile):
       def __init__(self, label, mediaType,**kw):
              super(SendMediaGroup, self).__init__(label, mediaType, **kw)
              self.medias =["Photo", "Video", "Document", "Audio"]
              self.mediaList = []
              self.typeOfMedia = MDExpansionPanel(content=ChoicePanel(commandNames=self.medias), panel_cls= MDExpansionPanelOneLine(text="Media Type"))
              self.box.add_widget(self.typeOfMedia, 3)
              self.buttonBox.add_widget(MDRaisedButton(text="Add to medias", pos_hint={'center_x': .1, 'top': 1}, on_press=self.addToMediaList))
              self.buttonBox.add_widget(MDRaisedButton(text="Edit medias", pos_hint={'center_x': .5, 'top': 1}, on_press= lambda x: changeScreen("Handle Media Group")))
              self.validate.pos_hint = {'center_x': .9, 'top': 1}
              

       def addToMediaList(self, button):
              if len(self.mediaList) == 10:
                     infoDialog(text="Media group can only contian 10 medias")
                     return
              caption = self.message.text
              mediaId = self.mediaID.text
              typeOfMedia = self.typeOfMedia.panel_cls.text
                     
              if len(mediaId) == 0:
                     self.mediaID.error = True
              else:
                     self.mediaID.error = False
              if typeOfMedia not in self.medias:
                     self.typeOfMedia.panel_cls.text = "Choose a media type"
              
              if len(mediaId) > 0 and typeOfMedia in self.medias:
                     allTypes = [media.get("type") for media in self.mediaList]
              
                     if len(allTypes) == 0:
                            self.mediaList.append({"type": typeOfMedia.lower(), "caption": caption, "media": mediaId})
                     elif typeOfMedia == "Photo" or typeOfMedia == "Video":
                            for type in allTypes:
                                   if type == "photo" or type == "video":
                                          continue
                                   else:
                                          infoDialog(text=f"Media group of {typeOfMedia} can only contain Photo and video")
                                          return
                            self.mediaList.append({"type": typeOfMedia.lower(), "caption": caption, "media": mediaId})
                     else:
                            if typeOfMedia.lower() not in allTypes:
                                   infoDialog(text=f"Media group of {typeOfMedia} can only contain {typeOfMedia}")
                                   return
                            else:
                                   self.mediaList.append({"type": typeOfMedia.lower(), "caption": caption, "media": mediaId})
                     self.message.text= ""
                     self.mediaID.text= ""
                     refreashMediaGroup()
       
       def addToCommandList(self, button):
              appDatas = appDatas = App.get_running_app().root.BotDatas.get('bot commands')
              commandName = self.commandName.text
              if len(commandName) == 0:
                     self.commandName.error = True
              else:
                     self.commandName.error = False

              if len(self.mediaList) < 2:
                     infoDialog(text=f"Media group must contain at least 2 media (media: {len(self.mediaList)}/10)")
                     
              
              if len(commandName) > 0 and len(self.mediaList) >= 2:
                     appDatas.append({"name": commandName, "command type": "Send media group", "displayed type": "Send Media Group", "args": {"media":self.mediaList.copy()}})
                     self.mediaList.clear()
                     self.commandName.text = ""
                     refreashMediaGroup()
                     refreshDataTable()
                     saveDatas()

              else:
                     return  
              
class BanWords(SendMessageScreen):
       def __init__(self, **kwargs):
              super().__init__("", **kwargs)
              self.box.remove_widget(self.messageBox)
              self.toolbar.title = "Ban words"
              self.commandName.hint_text = "Enter word(s) to ban"
              self.banTime = MDExpansionPanel(content=ChoicePanel(commandNames=BanTimes), panel_cls= MDExpansionPanelOneLine(text="Ban Time"))
              self.box.add_widget(self.banTime, 1)
              self.validate.text = "Add to banned words"
              
       def addToCommandList(self, button):
              words = self.commandName.text
              banTime= self.banTime.panel_cls.text
              if len(words) == 0:
                     self.commandName.error = True
              else:
                     self.commandName.error = False
              if banTime not in BanTimes:
                     infoDialog(text="Choose a ban time")

              if len(words) > 0 and banTime in BanTimes:
                     banList = App.get_running_app().root.BotDatas.get("ban words")
                     banList.append({"word": words, "time": banTime})
                     self.commandName.text = ""
                     refreshBanWords()
                     saveDatas()

class AdminsScreen(SendMessageScreen):
       def __init__(self, **kwargs):
              super().__init__("", **kwargs)
              self.toolbar.title = "Add Admins"
              self.commandName.hint_text = "Enter admin username (without the @)"
              self.box.remove_widget(self.messageBox)
              self.adminType = MDExpansionPanel(content=ChoicePanel(commandNames=["Admin", "Master"]), panel_cls= MDExpansionPanelOneLine(text="Admin"))
              self.box.add_widget(self.adminType, 1)
              self.validate.text = "Add Admin"

       def addToCommandList(self, button):
              adminList = App.get_running_app().root.BotDatas.get("bot admins")
              adminNames= [admin.get("name") for admin in adminList]
              master = App.get_running_app().root.BotDatas.get("master").get("name")
              name = self.commandName.text
              adminType = self.adminType.panel_cls.text
              if len(name) == 0:
                     self.commandName.error = True 
                     return
              if adminType == "Admin":
                     if name in adminNames:
                            infoDialog(text= f"{name} is already an admin")
                     else:
                            adminList.append({"name":name, "getAllId": False})
                            infoDialog(text= f"{name} is now an admin")
              elif adminType == "Master":
                     if name == master:
                            infoDialog(text= f"{name} is already the master")
                     else:
                            App.get_running_app().root.BotDatas.get("master")["name"] = name
                            infoDialog(text= f"{name} is the master")
                            if name not in adminNames:
                                   adminList.append({"name":name, "getAllId": False})
              self.commandName.text = ""
              self.adminType.panel_cls.text = "Admin"
              refreshAdmins()
              saveDatas()

class TokenScreen(SendMessageScreen):
       def __init__(self,  **kwargs):
              super().__init__("", **kwargs)   
              self.box.remove_widget(self.messageBox)   
              self.box.remove_widget(self.commandName)
              self.toolbar.title = "Bot Token" 
              self.entryBox = MDBoxLayout(size_hint=(.1, None), orientation= 'vertical')
              self.question_icon = MDIconButton(icon="help-circle", pos_hint={"top":1, "right": 1}, on_press= self.gotoToken)
              self.entryBox.add_widget(self.question_icon)
              self.entryBox.add_widget(self.commandName)
              self.commandName.hint_text ="Enter your bot's token" 
              self.validate.text = "Validate Token"    
              self.box.add_widget(self.entryBox, 1)

       def gotoToken(self, button):
              changeScreen("Help")
              #TODO Scroll to this section
              
       def addToCommandList(self, button):  
              token = self.commandName.text 
              if len(token) == 0:
                     self.commandName.error = True
                     return
              Clock.schedule_once(lambda dt: App.get_running_app().root.checkBot(token), .5)
# Send Message and child classes

# DataTables and child classes
class DataTable(Screen):
       def __init__(self,  commandList, columns, **kwargs):
              super(DataTable, self).__init__(**kwargs)
              self.commandList= commandList
              self.columns  = columns
              self.table = MDDataTable(
                     pos_hint = {'center_x': 0.5},
                     size_hint =(1, .8),
                     use_pagination=True,
                     check = True,
                     elevation = 0,
                     column_data = self.columns
              )

              
              self.layout = FloatLayout(size_hint=( 1, 1))
              self.deleteButton = MDRaisedButton(text="Delete", pos_hint= {'center_x': .05,'center_y': 0.07}, on_release=self.delete_button_press)
              self.toolbar = MainToolBar(title= "List Of Commands")
              self.layout.add_widget(self.toolbar)
              self.layout.add_widget(self.table)
              self.layout.add_widget(self.deleteButton)
              self.add_widget(self.layout)
              if self.__class__.__name__ == "DataTable":
                     self.mapData()

     
       def delete_button_press(self, button):       
              chekedItems = self.table.get_row_checks()
       
              indexes = [int(x[0])-1 for x in chekedItems]
              indexes.sort(reverse=True)
              if len(indexes) == 0:
                     return
              for index in indexes:
                     if index > len(self.commandList)-1:
                            return
                     else:
                            self.commandList.pop(index)
              self.mapData()
              saveDatas()
                

       def mapData(self):
              index = 1
              newRows = []
              for data in self.commandList:
                     if data.get("args"):
                            text = data.get("args").get("text")
                            textLength = len(text)
                            caption = f"{text[:80]}..." if textLength > 80 else text
                     if data.get("displayed type") == "Send Message":
                            newRows.append((index, data.get("displayed type"), data.get("name"), "", caption))
                     elif data.get("displayed type") in MediaTypes:
                            newRows.append((index, data.get("displayed type"), data.get("name"), data.get("args").get("fileId"), caption))
                     elif data.get("displayed type") == "Send Media Group":
                            ids = " ,".join([media.get("media") for media in data.get("args").get("media")])
                            newRows.append((index, data.get("displayed type"), data.get("name"), f"{ids[:25]}...", ""))
                     index+=1     
              self.table.row_data = newRows 

class HandleMediaGroup(DataTable):
       def __init__(self, mediaList, columns, **kwargs):
              super(HandleMediaGroup,self).__init__(mediaList, columns, **kwargs)
              self.toolbar.title  = "List Of Medias"
              self.toolbar.left_action_items = [["keyboard-backspace", lambda x: changeScreen("Media Group")]]
              self.mapData()
       
       def mapData(self):
              newRows = []
              index = 1
              for data in self.commandList:
                     caption = data.get("caption")
                     caption = f"{caption[:70]}..." if len(caption) > 70 else caption
                     newRows.append((index, data.get("type"), caption, data.get("media")))
                     index +=1
              self.table.row_data = newRows  

class BannedWord(DataTable):
       def __init__(self, bannedWords, columns, **kwargs):
              super().__init__(bannedWords, columns, **kwargs)
              self.toolbar.title  = "List Of Banned words"
              self.deleteButton.pos_hint= {'center_x': .1,'center_y': 0.05}
              self.mapData()  

       def mapData(self):
              newRows = []
              index = 1
              for data in self.commandList:
                     word = data.get('word')
                     word = f"{word[:20]}..." if len(word) > 20 else word
                     newRows.append((index, word, data.get("time") ))
                     index +=1
              self.table.row_data = newRows  
               
class AdminList(DataTable):
       def __init__(self, listOfAdmin, columns, **kwargs):
              super().__init__(listOfAdmin, columns, **kwargs)
              self.toolbar.title  = "List Of Admins"
              self.deleteButton.pos_hint= {'center_x': .1,'center_y': 0.05}
       
       def mapData(self):
              newRows = []
              index = 1
              for data in self.commandList:
                     status = "Master" if data.get("name") == App.get_running_app().root.BotDatas.get("master").get("name") else ""
                     name = data.get("name")
                     name = f"{name[:20]}..." if len(data.get("name")) > 20 else name
                     newRows.append((index, name, status))
                     index +=1   
              self.table.row_data = newRows    
# DataTables and child classes

# Panels---------------------------------------------------------------------------------
class ExpentionPanelContent(MDBoxLayout):
       def __init__(self, commandNames, **kwargs):
              super().__init__(**kwargs)
              self.orientation = "vertical"
              self.adaptive_height = True
              for name in commandNames:
                     self.add_widget(OneLineListItem(text=name, on_press=self.goto))

       def goto(self, inst):
              changeScreen(inst.text)

class ChoicePanel(ExpentionPanelContent)   :
       def __init__(self, commandNames, **kwargs):
              super(ChoicePanel, self).__init__(commandNames, **kwargs)   

       def goto(self, inst):
              self.parent.panel_cls.text = inst.text           
# Panels---------------------------------------------------------------------------------    
# Content
class TokenConfigContent(MDBoxLayout):
       def __init__(self, *args, **kwargs):
              super().__init__(*args, **kwargs)
              self.orientation = "vertical"
              self.adaptive_height = True
              self.tokenLabel = MDLabel(text="Save Token On Quit", pos_hint={'top': 1.0,'center_x': .50})
              self.tokenSwitch = MDSwitch(active=isSaveTokenEnabled(),  pos_hint={'top': 1,'right': .90})
              self.add_widget(self.tokenLabel)
              self.add_widget(self.tokenSwitch)
# Content
       
# Help
class HelpScreen(Screen):
       def __init__(self, **kw):
              super().__init__(**kw)
              self.titles = {}
              self.scrollview = MDScrollView(scroll_type=['bars', 'content'],bar_width='10dp')
              self.toolbar = MainToolBar()
              self.layout = MDBoxLayout(orientation= 'vertical',  size_hint_y=None)
              self.toolbar.title= "Help"
              self.layout.add_widget(self.toolbar)
              self.layoutSize = 400
              
              for index, help in enumerate(helps):
                     box1 = MDBoxLayout(orientation= 'vertical', spacing=10, padding=dp(10))
                     title = MDLabel(font_style="H6", halign="left",text= help.get("title"))
                     box1.add_widget(title)
                     self.titles[index] = title
                     content = MDLabel(halign="left",text= help.get("content"))
                     box1.add_widget(content)
                     box1.size[1] = box1.size[1] + title.size[1] + content.size[1]
                     self.layout.add_widget(box1)
                     self.layoutSize += box1.size[1]
                     #TODO need a better way to do this size alwais return [100, 100]
                    
              
              self.scrollview.add_widget(self.layout)
              self.add_widget(self.scrollview)
              self.layout.size= (Window.width, self.layoutSize)
              
       def scrollToTitle(self, title):
              self.scrollview.scroll_to(self.titles[title])

# Dashboard
class DashBoard(Screen):
       def __init__(self, **kw):
              super().__init__(**kw)
              self.toolbar = MainToolBar(title = "Dashboard")
              self.box = FloatLayout(size_hint_y= None,pos_hint={'top': .8}, size_hint_x= 1)
              
              self.startButton = MDRaisedButton(text="Start Bot", pos_hint={'right': .3, 'top': 1}, on_press= lambda x: startBot())
              self.stopButton = MDRaisedButton(text="Stop Bot", disabled = True, pos_hint={'right': .9, 'top': 1}, on_press= lambda x: stopBot())

              self.tokenConfig = MDRaisedButton(text="Token Config", pos_hint={'top': .4,'right' : 0.35}, halign="center", on_press= lambda x: self.tokenModal.open())
              self.tokenModal = MDDialog(title="Token Configuration",type= 'custom', content_cls=TokenConfigContent(), size_hint= (0.9, None),
                                         buttons= [MDFlatButton(text= 'cancel', on_release=lambda x: self.tokenModal.dismiss()), MDRaisedButton(text= 'save', on_release=self.saveTokenConfig)])

              self.filesButton = MDRaisedButton(text="Bot Files", pos_hint={'right': .3, 'top': -.2}, on_press= lambda x: self.fileDropdown.open())
              self.webhookButton = MDRaisedButton(text="Configure Webhook", disabled = True, pos_hint={'right': .9, 'top': -.2})
              self.fileDropdown = MDDropdownMenu(items=DropdownBotItems, caller=self.filesButton, width_mult= 3)

              self.box.add_widget(self.startButton)
              self.box.add_widget(self.stopButton)
              self.box.add_widget(self.tokenConfig)
              self.box.add_widget(self.filesButton)
              self.box.add_widget(self.webhookButton)
              
              self.add_widget(self.toolbar)
              self.add_widget(self.box)

       def saveTokenConfig(self, button):
              switchValue = self.tokenModal.content_cls.tokenSwitch.active
              if switchValue == False:
                     deleteToken()
              else:
                     token = App.get_running_app().root.Bot.botToken
                     if len(token) != 0:
                            saveToken(token)

              toggleEnableSave(switchValue)
              self.tokenModal.dismiss()
# Nav drawer
class NavigationDrawer(MDNavigationDrawer):
       def __init__(self, **kwargs):
              super(NavigationDrawer, self).__init__(**kwargs)
              individualItems = ["Token", "Command List"]
              self.drawerHeader = MDNavigationDrawerHeader(title="Bot: ", text="Status: offline", title_font_size="26sp")
              self.drawerMenu = MDNavigationDrawerMenu()
              self.drawerMenu.add_widget(self.drawerHeader)  
              self.panels = (self.commandsPanel, self.adminPanel, self.banPanel) = (MDExpansionPanel(content=ExpentionPanelContent(commandNames=BotCommands), panel_cls= MDExpansionPanelOneLine(text="Bot Commands")), 
                                                                                    MDExpansionPanel(content=ExpentionPanelContent(commandNames=["Add Admin", "List Of Admin"]), panel_cls= MDExpansionPanelOneLine(text="Admins")),
                                                                                    MDExpansionPanel(content=ExpentionPanelContent(commandNames=["Ban words", "Banned Words"]), panel_cls= MDExpansionPanelOneLine(text="Ban")))
              # Will add all the individual items at once       
              for item in individualItems:
                     self.drawerMenu.add_widget(OneLineListItem(text = item, on_press=lambda x: changeScreen(x.text)))
              for panel in self.panels:
                     self.drawerMenu.add_widget(panel)
              # Will add here the panels the help item will remain at the bottom
              self.drawerMenu.add_widget(OneLineListItem(text = "Help", on_press=lambda x: changeScreen(x.text)))
              
       
              self.add_widget(self.drawerMenu)

# Screen manager
class WindowsManager(ScreenManager):
       def __init__(self, BotDatas, **kwargs):
              super(WindowsManager, self).__init__(**kwargs)
              self.sendMessage = SendMessageScreen(label="Send Message", name = "Send Message")
              self.sendImage = SendFile(label="Send Image", mediaType="Image", name= "Send Image")
              self.sendVideo = SendFile(label="Send Video", mediaType="Video", name= "Send Video")
              self.sendFile = SendFile(label="Send File", mediaType="File", name= "Send File")
              self.sendAudio = SendFile(label="Send Audio", mediaType="Audio", name= "Send Audio")
              self.mediaGroup = SendMediaGroup(name= "Media Group", label="Send Media Group", mediaType="Media Group")
              self.token = TokenScreen(name="Token")
              self.dataTable = DataTable(name="Command List", commandList=BotDatas.get("bot commands"), columns=commandListCols)
              self.handleMediaGroup = HandleMediaGroup(name="Handle Media Group", mediaList=self.mediaGroup.mediaList, columns=mediaGroupCols)
              self.banWords = BanWords(name="Ban words")
              self.bannedWords = BannedWord(name="Banned Words", columns=bannedWordsCols, bannedWords=BotDatas.get("ban words"))
              self.addAdmin = AdminsScreen(name="Add Admin")
              self.adminList = AdminList(name="List Of Admin", columns=adminListCols, listOfAdmin=BotDatas.get("bot admins")) 
              self.dashboard = DashBoard(name="Dashboard")
              self.help = HelpScreen(name="Help")


              self.add_widget(self.dashboard)
              self.add_widget(self.sendMessage)
              self.add_widget(self.sendImage)
              self.add_widget(self.sendVideo)
              self.add_widget(self.sendFile)
              self.add_widget(self.sendAudio)
              self.add_widget(self.mediaGroup)
              self.add_widget(self.token)
              self.add_widget(self.dataTable)
              self.add_widget(self.handleMediaGroup)
              self.add_widget(self.banWords)
              self.add_widget(self.bannedWords)
              self.add_widget(self.addAdmin)
              self.add_widget(self.adminList)
              self.add_widget(self.help)


# Root widget
class NavLayout(MDNavigationLayout):
       def __init__(self, *args, **kwargs):
              super().__init__(*args, **kwargs)
              Window.size = (450, 600)
              self.botToken = loadToken()
              self.BotDatas = loadCommandList()
              self.Bot = TelegramBot(botDatas=self.BotDatas, botToken=self.botToken)
              self.navigationDrawer = NavigationDrawer(close_on_click=True)
              self.screenmanager = WindowsManager(BotDatas=self.BotDatas)
              self.add_widget(self.screenmanager)
              self.add_widget(self.navigationDrawer)


       def handleError(self, text):
              #TODO Find a way to show the error on the main thread
              infoDialog(text)
              self.stopBot()
       
       def checkBot(self, token):
              bot = App.get_running_app().root.Bot
              isBot = bot.getMe(token=token)

              if isBot == "error":
                     self.Bot.botToken = ""
                     return
              if isBot.get("ok"):
                     infoDialog(text= f"Your bot {isBot.get('result').get('first_name')} is ready to use", title= f"Bot username: {isBot.get('result').get('username')}")
                     bot.botToken = token
                     changeHeader(title=f"Bot: {isBot.get('result').get('first_name')}")
                     if isSaveTokenEnabled():
                            saveToken(token)
                     
              else:
                     infoDialog(text= "Bot not found make sure you enter the token right")
                     self.Bot.botToken = ""
                     pass

       def handleUpdates(self, *args):
              thread = threading.Thread(target=self.Bot.handleUpdates)
              thread.start()
       
       def startBot(self):
              if len(self.Bot.botToken) == 0:
                     changeScreen("Token")
                     infoDialog(text="Insert your bot token")
                     return
              self.screenmanager.dashboard.startButton.disabled=True
              self.screenmanager.dashboard.stopButton.disabled=False
              changeHeader(text="Status: online")
              self.clock = Clock.schedule_interval(self.handleUpdates, 4)
       
       def stopBot(self):
              if "clock" in dir(self):
                     self.clock.cancel()
                     changeHeader(text="Status: offline")
                     try:
                            self.screenmanager.dashboard.stopButton.disabled=True
                            self.screenmanager.dashboard.startButton.disabled=False
                     except:
                            pass

       def checkStatus(self, *args):
              if "clock" not in dir(self):
                     self.screenmanager.dashboard.startButton.disabled=False
                     self.screenmanager.dashboard.stopButton.disabled=True
              else:
                     if self.clock.is_triggered == True:
                            self.screenmanager.dashboard.startButton.disabled=True
                            self.screenmanager.dashboard.stopButton.disabled=False
                     else:
                            self.screenmanager.dashboard.startButton.disabled=False
                            self.screenmanager.dashboard.stopButton.disabled=True

       def loadFile(self):
              closeFilesDropdown()
              self.fileManager = MDFileManager(exit_manager=self.exitManager,select_path=self.loadSelected)
              self.fileManager.show(loadPath())
              
       def saveData(self):
              closeFilesDropdown()
              self.fileManager = MDFileManager(exit_manager=self.exitManager,select_path=self.saveInPath)
              self.fileManager.show(loadPath())
              self.fileName.open()

       def exitManager(self, instance):
              self.fileManager.close()

       def saveInPath(self, path):
              fileName= "BotDatas.json" if len(self.fileName.content_cls.entry.text)==0 else self.fileName.content_cls.entry.text
              savePath(path)
              if os.path.isfile(path):
                     infoDialog("Select A Directory Not A File")
                     return
              try:
                     with open(path+f"\{fileName}", "w") as f:
                            json.dump(self.BotDatas, f)

                     self.fileManager.close()
                     
              except Exception as e:
                     infoDialog("Error Could Not Save Your Datas")
                     
       def loadSelected(self, path):
              savePath(path)
              keys = ["master", "bot commands", "ban words", "bot admins"]       
              try: 
                     with open(path, "r") as f:
                            newDatas = json.load(f)
                            if type(newDatas) == dict:
                                   for key in keys:
                                          if key not in newDatas.keys():
                                                 infoDialog(text="Invalid Data File")
                                                 return
                                   for key in newDatas.keys():
                                          if key == "master" and type(newDatas.get(key)) != dict:
                                                 infoDialog(f"Invalid Key In {path}")
                                                 return
                                          elif key != "master" and type(newDatas.get(key)) != list:
                                                 infoDialog(f"Invalid Key In {path}")
                                                 return

                            self.BotDatas = newDatas
                            self.screenmanager.dataTable.commandList = self.BotDatas.get("bot commands")
                            self.screenmanager.adminList.commandList = self.BotDatas.get("bot admins")
                            self.screenmanager.bannedWords.commandList = self.BotDatas.get("ban words")
                            refreshDataTable()
                            refreshAdmins()
                            refreshBanWords()
                            saveDatas()
                                   
              except:
                     infoDialog(text="Invalid Or Corrupted File")
                     pass
              self.fileManager.close()
                     
       def getServerFiles(self):
              closeFilesDropdown()
              self.fileManager = MDFileManager(exit_manager=self.exitManager,select_path=self.copyFiles)
              self.fileManager.show(loadPath())

       def copyFiles(self, path):
              savePath(path)
              destination = path + "/bot"
              source = os.getcwd() + "/bot"
              shutil.copytree(source, destination)
              shutil.copyfile(os.getcwd()+"/config.ini", destination+"/config.ini")
              with open(destination + "/BotDatas.json", "w") as f:
                     json.dump(self.BotDatas, f)

# App            
class TelebotManagerApp(MDApp):
       def build(self):
              title = "Telegram Bot Manager"
              self.title = title
              self.navigationLayout = NavLayout()
              return self.navigationLayout

       def on_stop(self):
              pass 
       
App = TelebotManagerApp()

if __name__ == "__main__":
       App.run()