import wx

_TRAY_ICON = r"im\Orb_of_Chance.png"
_TRAY_TOOLTIP = "What are the chances?"

class Main(wx.TaskBarIcon):
    def __init__(self, app):
        super(Main, self).__init__()
        self.set_icon(_TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_BALLOON_CLICK, self.on_balloon_click)
        self._app = app

        self.new_recipe_skeleton = "Heyya, you've got new recipes:\n\n%s"

    @staticmethod
    def create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, wx.ID_ANY, label)
        menu.Bind(wx.EVT_MENU, func, id = item.GetId())
        menu.AppendItem(item)
        return item

    def CreatePopupMenu(self):
        menu = wx.Menu()
        self.create_menu_item(menu, "Show recipes", self.on_show)
        menu.AppendSeparator()
        self.create_menu_item(menu, "Exit", self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, _TRAY_TOOLTIP)

    def on_left_down(self, event):
        self.on_show()

    def on_balloon_click(self, event):
        self._app.launch_mainframe()

    def on_show(self, event = None):
        #lol why is this a separate function?
        self._app.launch_mainframe()
        
    def on_exit(self, event):
        self._app.quit()
    
    def new_recipes(self, recipelist):
        recipes = [
            recipe[0]["name"] + ", [" + ", ".join(
                [item["_tab_label"] 
                 for item 
                 in recipe]
                ) + "]" 
            for recipe 
            in recipelist
            ]
        reprcipe = "\n".join(recipes[:4])
        if len(recipes) > 4:
            reprcipe += "\nPlus %s more..." % (len(recipes) - 4)

        self.ShowBalloon("New recipes!",
                         self.new_recipe_skeleton % reprcipe)
