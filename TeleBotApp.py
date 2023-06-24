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






from TelegramBot import TelegramBot
from Config import saveCommandList, loadCommandList, saveToken, loadToken, toggleEnableSave, isSaveTokenEnabled, deleteToken, savePath, loadPath

# The main commands of the bots
BotCommands = ["Send Message", "Send Image", "Send Video", "Send File", "Send Audio", "Media Group"]
# Will add more screen to those lists
largeScreens = ["Command List"]
longScreens  = [*BotCommands, "Help"]

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

       def addToCommandList(self, inst):
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
                            #TODO save the datas
                     else:  
                            if self.mediaType == "Image":
                                   appDatas.append({"name": commandName, "command type": "Send image", "displayed type": "Send Image", "args": {"caption": caption, "fileId":self.mediaID.text}})
                            else:
                                   appDatas.append({"name": commandName, "command type": "Send document", "displayed type": f"Send {self.mediaType}", "args": {"caption": caption, "fileId":self.mediaID.text}})
                            #TODO save the datas
                            self.mediaID.text = ""
                     self.commandName.text = ""
                     self.message.text = ""
                     #TODO refresh the datatable
                     
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
             
# Nav drawer
class NavigationDrawer(MDNavigationDrawer):
       def __init__(self, **kwargs):
              super(NavigationDrawer, self).__init__(**kwargs)
              individualItems = ["Command List"]
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
              self.testScreen = SendMessageScreen("Send Message")
              self.add_widget(self.testScreen)


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