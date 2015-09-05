import wx

class Main(wx.Frame):
    def __init__(self, app, local_version, remote_version, patch_notes,
                 position, size):
        self._app = app
        local_version = str(local_version)
        remote_version = str(remote_version)

        wx.Frame.__init__(self, None, id = wx.ID_ANY, title = u"Update available", pos = position, size = size, style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        sizer_bg = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_bg = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_bg.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        self.static_update_available = wx.StaticText(self.panel_bg, wx.ID_ANY, u"A new update is available, would you like to update now?", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_update_available.Wrap(-1)
        sizer_main.Add(self.static_update_available, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        sizer_version_info = wx.BoxSizer(wx.HORIZONTAL)
        
        self.static_your_version = wx.StaticText(self.panel_bg, wx.ID_ANY, u"Your version:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_your_version.Wrap(-1)
        sizer_version_info.Add(self.static_your_version, 0, wx.ALL, 5)
        
        self.label_your_version = wx.StaticText(self.panel_bg, wx.ID_ANY, local_version, wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_your_version.Wrap(-1)
        self.label_your_version.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString))
        
        sizer_version_info.Add(self.label_your_version, 0, wx.ALL, 5)
        
        
        sizer_version_info.AddSpacer((20, 0), 1, wx.EXPAND, 5)
        
        self.static_latest_version = wx.StaticText(self.panel_bg, wx.ID_ANY, u"Latest version:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_latest_version.Wrap(-1)
        sizer_version_info.Add(self.static_latest_version, 0, wx.ALL, 5)
        
        self.label_latest_version = wx.StaticText(self.panel_bg, wx.ID_ANY, remote_version, wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_latest_version.Wrap(-1)
        self.label_latest_version.SetFont(wx.Font(wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString))
        
        sizer_version_info.Add(self.label_latest_version, 0, wx.ALL, 5)
        
        
        sizer_main.Add(sizer_version_info, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        sizer_patch_notes = wx.BoxSizer(wx.VERTICAL)
        
        self.static_patch_notes = wx.StaticText(self.panel_bg, wx.ID_ANY, u"Patch notes:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_patch_notes.Wrap(-1)
        sizer_patch_notes.Add(self.static_patch_notes, 0, wx.TOP | wx.RIGHT | wx.LEFT, 5)
        
        self.text_patch_notes = wx.TextCtrl(self.panel_bg, wx.ID_ANY, patch_notes, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY)
        sizer_patch_notes.Add(self.text_patch_notes, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        
        
        sizer_main.Add(sizer_patch_notes, 10, wx.EXPAND, 5)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        sizer_actions = wx.BoxSizer(wx.HORIZONTAL)
        
        self.button_ignore = wx.Button(self.panel_bg, wx.ID_ANY, u"Don't tell me about this one again", wx.DefaultPosition, wx.DefaultSize, 0)
        sizer_actions.Add(self.button_ignore, 1, wx.ALL, 5)
        
        self.button_update = wx.Button(self.panel_bg, wx.ID_ANY, u"Update to this version right now", wx.DefaultPosition, wx.DefaultSize, 0)
        sizer_actions.Add(self.button_update, 1, wx.ALL, 5)
        
        
        sizer_main.Add(sizer_actions, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        self.panel_bg.SetSizer(sizer_main)
        self.panel_bg.Layout()
        sizer_main.Fit(self.panel_bg)
        sizer_bg.Add(self.panel_bg, 1, wx.EXPAND, 5)
        
        
        self.SetSizer(sizer_bg)
        self.Layout()

        self.setbinds()

        self.Show()

    def setbinds(self):
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.button_ignore.Bind(wx.EVT_BUTTON, self.on_ignore)
        self.button_update.Bind(wx.EVT_BUTTON, self.on_update)

    def _on_close(self, event):
        x, y = self.GetPosition()
        w, h = self.GetSize()
        self._app.update_window_closed(x, y, w, h)
        event.Skip()

    def on_ignore(self, event):
        self._app.ignore_update()
        self.Close()

    def on_update(self, event):
        self._app.update()
        self.Close()