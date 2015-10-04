import threading

import wx
import wx.lib.newevent

import acquisition

class LeagueFinder(threading.Thread):
    def __init__(self, frame, evt_complete):
        super(LeagueFinder, self).__init__()
        self._frame = frame
        self._evt_complete = evt_complete

    def run(self):
        evt = self._evt_complete(leagues = acquisition.get_leagues())
        try:
            wx.PostEvent(self._frame, evt)
        except TypeError: #closed the window before the leagues were checked
            pass

class Main(wx.Frame):
    def __init__(self, app, current_league):
        self._app = app
        self._updated = True
        self._current_league = current_league

        if self._app.settings["stash_tabs"]:
            lowest = self._app.settings["stash_tabs_lowest"]
            highest = self._app.settings["stash_tabs_highest"]
            extras = ",".join(self._app.settings["stash_tabs_extras"])
        else:
            lowest = 0
            highest = 65
            extras = ""

        if "stash_tabs_filter" in self._app.settings:
            filtered = self._app.settings["stash_tabs_filter"]
        else:
            filtered = True

        wx.Frame.__init__(self, parent = None, id = wx.ID_ANY, title = u"Settings :D", pos = wx.DefaultPosition, size = wx.Size(-1,-1), style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        sizer_bg = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_bg = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_bg.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        sizer_centred = wx.BoxSizer(wx.VERTICAL)

        group_league = wx.StaticBoxSizer(wx.StaticBox(self.panel_bg, wx.ID_ANY, u"League"), wx.VERTICAL)
        
        self.choice_league = wx.Choice(self.panel_bg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, [], 0)
        self.choice_league.SetSelection(999)
        self.choice_league.Enable(False)
        group_league.Add(self.choice_league, 0, wx.ALL | wx.EXPAND, 5)
        
        
        sizer_centred.Add(group_league, 1, wx.EXPAND, 5)
        
        
        sizer_centred.AddSpacer((0, 15), 0, 0, 5)
        
        self.check_filter = wx.CheckBox(self.panel_bg, wx.ID_ANY, u"Filter tabs?", wx.DefaultPosition, wx.DefaultSize, 0)
        self.check_filter.SetValue(filtered)
        sizer_centred.Add(self.check_filter, 0, wx.ALL, 5)

        
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
        
        self.line_settings_actions = wx.StaticLine(self.panel_bg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        sizer_centred.Add(self.line_settings_actions, 0, wx.EXPAND | wx.ALL, 5)
        
        sizer_actions = wx.BoxSizer(wx.HORIZONTAL)
        
        self.static_hint = wx.StaticText(self.panel_bg, wx.ID_ANY, u"Settings are saved automatically :3", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_hint.Wrap(-1)
        sizer_actions.Add(self.static_hint, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        
        sizer_actions.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.button_check_for_updates = wx.Button(self.panel_bg, wx.ID_ANY, u"Check for updates", wx.DefaultPosition, wx.DefaultSize, 0)
        sizer_actions.Add(self.button_check_for_updates, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        
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

        self.update_interface()

        got_leagues, self.evt_got_leagues = wx.lib.newevent.NewEvent()

        self.setbinds()

        LeagueFinder(self, got_leagues).start()

        self.Show()

    def setbinds(self):
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.Bind(wx.EVT_IDLE, self._on_idle)
        self.Bind(self.evt_got_leagues, self._got_leagues)
        self.choice_league.Bind(wx.EVT_CHOICE, self._on_league)
        self.check_filter.Bind(wx.EVT_CHECKBOX, self._on_filter)
        self.spin_from.Bind(wx.EVT_SPINCTRL, self._on_updated)
        self.spin_to.Bind(wx.EVT_SPINCTRL, self._on_updated)
        self.text_unnumbered.Bind(wx.EVT_TEXT, self._on_updated)
        self.button_check_for_updates.Bind(wx.EVT_BUTTON, self._on_check)

    def _on_updated(self, event = None):
        self._updated = True

    def _on_idle(self, event):
        if self._updated:
            lowest = self.spin_from.GetValue()
            highest = self.spin_to.GetValue()
            extras = [tabname.strip() for tabname in 
                      self.text_unnumbered.GetValue().split(",")]
            stash_tabs = [str(x) for x in xrange(lowest, highest + 1)]
            stash_tabs.extend(extras)
            league = self.choice_league.GetStringSelection()
            filter_tabs = self.check_filter.GetValue()
            if league:
                self._app.settings["league"] = league
            self._app.settings["stash_tabs"] = stash_tabs
            self._app.settings["stash_tabs_lowest"] = lowest
            self._app.settings["stash_tabs_highest"] = highest
            self._app.settings["stash_tabs_extras"] = extras
            self._app.settings["stash_tabs_filter"] = filter_tabs
            self._app.recheck_items()
            self._updated = False

    def _got_leagues(self, event):
        self.choice_league.SetItems(event.leagues)
        if self._current_league:
            self.choice_league.SetStringSelection(self._current_league)
        self.choice_league.Enable()

    def _on_league(self, event):
        self._on_updated()
        self._app.recheck_items()

    def _on_filter(self, event):
        self._on_updated()

        self.update_interface()

    def update_interface(self):
        enable = self.check_filter.GetValue()

        for widget in [self.spin_from, self.spin_to, self.text_unnumbered]:
            widget.Enable(enable)

    def _on_check(self, event):
        self._app.check_for_updates()

    def _on_close(self, event):
        self._app.settings_window_closed()
        event.Skip()