import wx

_TRAY_ICON = r"im\Orb_of_Chance.png"
_TRAY_TOOLTIP = "What are the chances?"

class Main(wx.TaskBarIcon):
    def __init__(self, app):
        super(Main, self).__init__()
        self.set_icon(_TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_show)
        self.Bind(wx.EVT_TASKBAR_BALLOON_CLICK, self.on_balloon_click)
        self._app = app

        self.balloonhandlers = {
            "update": self._app.launch_update_window,
            "recipes": self._app.launch_mainframe,
            }
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
        self.create_menu_item(menu, "Settings", self.on_settings)
        if self._app.update_available:
            self.create_menu_item(menu, "Update", self.on_update)
        else:
            self.create_menu_item(menu, "Check for updates", self.on_check)
        menu.AppendSeparator()
        self.create_menu_item(menu, "Exit", self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, _TRAY_TOOLTIP)

    def on_balloon_click(self, event):
        self.balloonhandler()

    def on_show(self, event = None):
        #lol why is this a separate function?
        self._app.launch_mainframe()

    def on_settings(self, event):
        self._app.launch_settings_window()

    def on_update(self, event):
        self._app.launch_update_window()

    def on_check(self, event):
        self._app.check_for_updates()
        
    def on_exit(self, event):
        self._app.quit()
    
    def new_recipes(self, recipelist):
        self.balloonhandler = self.balloonhandlers["recipes"]
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

    def update_available(self):
        self.balloonhandler = self.balloonhandlers["update"]
        self.ShowBalloon("New version!",
                         ("A new version, %s, is available.  Click here to see"
                          " the patch notes.") % self._make_remote_version())

    def _make_remote_version(self):
        try:
            return ".".join([str(x) for x in self._app.remote_version])
        except:
            return str(self._app.remote_version)