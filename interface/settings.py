import wx

class Main(wx.Frame):
    def __init__(self, app):
        self._app = app
        self._updated = True

        if self._app.settings["stash_tabs"]:
            lowest = self._app.settings["stash_tabs_lowest"]
            highest = self._app.settings["stash_tabs_highest"]
            extras = ",".join(self._app.settings["stash_tabs_extras"])
        else:
            lowest = 0
            highest = 65
            extras = ""

        wx.Frame.__init__(self, parent = None, id = wx.ID_ANY, title = u"Settings :D", pos = wx.DefaultPosition, size = wx.Size(-1,-1), style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        sizer_bg = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_bg = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_bg.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        sizer_centred = wx.BoxSizer(wx.VERTICAL)
        
        group_numbered = wx.StaticBoxSizer(wx.StaticBox(self.panel_bg, wx.ID_ANY, u"Numbered tabs to check:"), wx.HORIZONTAL)
        
        self.static_from = wx.StaticText(self.panel_bg, wx.ID_ANY, u"From:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_from.Wrap(-1)
        group_numbered.Add(self.static_from, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.spin_from = wx.SpinCtrl(self.panel_bg, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10000, lowest)
        group_numbered.Add(self.spin_from, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.static_to = wx.StaticText(self.panel_bg, wx.ID_ANY, u"To:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_to.Wrap(-1)
        group_numbered.Add(self.static_to, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        self.spin_to = wx.SpinCtrl(self.panel_bg, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10000, highest)
        group_numbered.Add(self.spin_to, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        
        sizer_centred.Add(group_numbered, 0, 0, 5)
        
        group_unnumbered = wx.StaticBoxSizer(wx.StaticBox(self.panel_bg, wx.ID_ANY, u"Other tabs to check (separated by commas):"), wx.VERTICAL)
        
        self.text_unnumbered = wx.TextCtrl(self.panel_bg, wx.ID_ANY, extras, wx.DefaultPosition, wx.DefaultSize, 0)
        group_unnumbered.Add(self.text_unnumbered, 0, wx.ALL | wx.EXPAND, 5)
        
        
        sizer_centred.Add(group_unnumbered, 0, wx.EXPAND, 5)
        
        sizer_actions = wx.BoxSizer(wx.VERTICAL)
        
        self.button_check_for_updates = wx.Button(self.panel_bg, wx.ID_ANY, u"Check for updates", wx.DefaultPosition, wx.DefaultSize, 0)
        sizer_actions.Add(self.button_check_for_updates, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        
        sizer_centred.Add(sizer_actions, 1, wx.EXPAND, 5)
        
        
        sizer_main.Add(sizer_centred, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        
        self.panel_bg.SetSizer(sizer_main)
        self.panel_bg.Layout()
        sizer_main.Fit(self.panel_bg)
        sizer_bg.Add(self.panel_bg, 1, wx.EXPAND, 5)
        
        
        self.SetSizer(sizer_bg)
        self.Layout()
        sizer_bg.Fit(self)

        self.setbinds()

        self.Show()

    def setbinds(self):
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_IDLE, self._on_idle)
        self.spin_from.Bind(wx.EVT_SPIN, self._on_updated)
        self.spin_to.Bind(wx.EVT_SPIN, self._on_updated)
        self.text_unnumbered.Bind(wx.EVT_TEXT, self._on_updated)
        self.button_check_for_updates.Bind(wx.EVT_BUTTON, self._on_check)

    def _on_updated(self, event):
        self._updated = True

    def _on_idle(self, event):
        if self._updated:
            lowest = self.spin_from.GetValue()
            highest = self.spin_to.GetValue()
            extras = [tabname.strip() for tabname in 
                      self.text_unnumbered.GetValue().split(",")]
            stash_tabs = [str(x) for x in xrange(lowest, highest + 1)]
            stash_tabs.extend(extras)
            self._app.settings["stash_tabs"] = stash_tabs
            self._app.settings["stash_tabs_lowest"] = lowest
            self._app.settings["stash_tabs_highest"] = highest
            self._app.settings["stash_tabs_extras"] = extras
            self._updated = False

    def _on_check(self, event):
        self._app.check_for_updates()

    def _on_close(self, event):
        self._app.settings_window_closed()
        event.Skip()