from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawer, MDNavigationDrawerHeader
from kivy.uix.screenmanager import Screen, ScreenManager



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

# Nav drawer
class NavigationDrawer(MDNavigationDrawer):
       def __init__(self, **kwargs):
              super(NavigationDrawer, self).__init__(**kwargs)
              individualItems = ["Command List"]
              self.drawerHeader = MDNavigationDrawerHeader(title="Bot: ", text="Status: offline", title_font_size="26sp")
              self.drawerMenu = MDNavigationDrawerMenu()
              self.drawerMenu.add_widget(self.drawerHeader)  
              # Will add all the individual items at once       
              for item in individualItems:
                     self.drawerMenu.add_widget(OneLineListItem(text = item, on_press=lambda x: changeScreen(x.text)))

              # Will add here the panels the help item will remain at the bottom
              self.drawerMenu.add_widget(OneLineListItem(text = "Help", on_press=lambda x: changeScreen(x.text)))
              
       
              self.add_widget(self.drawerMenu)
              
             

# Screen manager
class WindowsManager(ScreenManager):
       def __init__(self, BotDatas, **kwargs):
              super(WindowsManager, self).__init__(**kwargs)


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