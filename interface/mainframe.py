import os
import json

import wx
import pygame
import pygame.gfxdraw

import img

#region colours
_col_grid = pygame.color.Color(104, 104, 104)
_col_itemname = pygame.color.Color(254, 254, 118)
_col_mod = pygame.color.Color(135, 135, 254)
#endregion

#region grid
grid = pygame.surface.Surface((119, 119))
grid.fill(0x000000)
interested = pygame.color.Color(255, 126, 44)
uninterested = pygame.color.Color(64, 30, 26)
for offset in xrange(10, 119, 10):
    pygame.gfxdraw.line(grid, offset - 1, 0, offset - 1, 119, _col_grid)
    pygame.gfxdraw.line(grid, 0, offset - 1, 119, offset - 1, _col_grid)
    if offset % 20 == 0:
        pygame.gfxdraw.line(grid, offset, 0, offset, 119, _col_grid)
    if offset % 60 == 0:
        pygame.gfxdraw.line(grid, 0, offset, 119, offset, _col_grid)
#endregion

#region itempreview
pygame.font.init()
_font = pygame.font.Font("font/Fontin-SmallCaps.ttf", 16)
_line = pygame.image.load("im/line.png")
_rare_l = pygame.image.load("im/rare_left.png")
_rare_m = pygame.image.load("im/rare_mid.png")
_rare_r = pygame.image.load("im/rare_right.png")
_sockets = {
    "R": pygame.image.load("im/R.png"),
    "G": pygame.image.load("im/G.png"),
    "B": pygame.image.load("im/B.png"),
    "W": pygame.image.load("im/W.png")
    }
_link = pygame.image.load("im/link.png")
_pad = 3
_spacer = pygame.surface.Surface((1, _pad))
#endregion

def make_socket_preview(item):
    if "links" not in item:
        return pygame.surface.Surface((0, 0))

    colours = item["links"][::2] #"R-G-B W" -> "RGBW"
    links = item["links"][1::2]  #"R-G-B W" -> "-- "
    socketcount = len(colours)
    if not socketcount:
        return pygame.surface.Surface((0, 0))

    w = ((socketcount - 1) * 74) + 57
    h = 57

    preview = pygame.surface.Surface((w, h))

    x = 0
    for socket in colours:
        preview.blit(_sockets[socket], (x, 0))
        x += 74

    x = 37
    for link in links:
        if link == "-":
            preview.blit(_link, (x, 16))
        x += 74

    return preview

def make_itempreview(item):
    name = _font.render(item["name"], True, _col_itemname)
    itemtype = _font.render(item["typeLine"], True, _col_itemname)

    mods = []
    for mod in item["explicitMods"]:
        surf = _font.render(mod, True, _col_mod)
        mods.append(surf)

    sockets = make_socket_preview(item)

    w = max(name, itemtype, sockets, *mods,
            key = lambda surf: surf.get_width()).get_width()
    h = 0
    for surf in name, itemtype, _line:
        h += surf.get_height()
    for surf in mods:
        h += surf.get_height()

    layout = []
    layout.extend([name, itemtype, _line])
    layout.extend(mods)
    layout.extend([_line, _spacer, sockets, _spacer])

    h = 0
    for component in layout:
        h += component.get_height()

    preview = pygame.surface.Surface((w, h))
    preview.fill(0x000000)

    x = _rare_l.get_width()
    end = w - _rare_r.get_width()
    while x < end:
        preview.blit(_rare_m, (x, 0))
        x += _rare_m.get_width()

    preview.blit(_rare_l, (0, 0))
    preview.blit(_rare_r, (end, 0))

    y = _pad
    for component in layout:
        x = (w - component.get_width()) / 2
        preview.blit(component, (x, y))
        y += component.get_height()

    return preview

class Main(wx.Frame):
    def __init__(self, app, position, size, maximised):
        self._app = app
        self._tab_previews = {}
        self._resized = False
        self._hoverpreview = None
        self._ignored_items = []
        self.cache_itempreviews = {}

        wx.Frame.__init__(self, parent = None, id = wx.ID_ANY, title = u"What are the chances?", pos = position, size = size, style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        sizer_bg = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_bg = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_bg.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        
        sizer_main = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer_info = wx.BoxSizer(wx.VERTICAL)
        
        self.tree_inventories = wx.TreeCtrl(self.panel_bg, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1,600), wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT)
        self.tree_inventories.SetQuickBestSize(False)

        self.tree_inventories.rootid = self.tree_inventories.AddRoot("root")
        self.tree_inventories.SetMinSize((250, -1))
        
        sizer_info.Add(self.tree_inventories, 1, wx.ALL | wx.EXPAND, 5)
        
        self.button_show_updated = wx.Button(self.panel_bg, wx.ID_ANY, u"More up to date info available", wx.DefaultPosition, wx.DefaultSize, 0)
        self.button_show_updated.Hide()
        
        sizer_info.Add(self.button_show_updated, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, 5)
        
        sizer_main.Add(sizer_info, 1, wx.EXPAND, 5)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.panel_items = wx.Panel(self.panel_bg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        grid_items = wx.GridSizer(0, 6, 0, 0)
        
        self.previews = [[None for _ in xrange(3)] for __ in xrange(6)]
        for y in xrange(3):
            col = []
            for x in xrange(6):
                preview = {}
                preview["sizer"] = wx.StaticBoxSizer(wx.StaticBox(self.panel_items, wx.ID_ANY, " "), wx.VERTICAL)
                panel = wx.Panel(self.panel_items, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)
                sizer = wx.BoxSizer(wx.VERTICAL)
                preview["bitmap"] = wx.StaticBitmap(panel, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size(120, 120), 0)
                img.show_pygame_surf_in_wxBitmap(grid, preview["bitmap"])
                sizer.Add(preview["bitmap"], 0, 0, 5)
                panel.SetSizer(sizer)
                panel.Layout()
                sizer.Fit(panel)
                preview["sizer"].Add(panel, 0, wx.ALL, 5)
                grid_items.Add(preview["sizer"], 0, 0, 5)

                preview["bitmap"].item = None
                
                self.previews[x][y] = preview

        self.panel_items.SetSizer(grid_items)
        self.panel_items.Layout()
        grid_items.Fit(self.panel_items)
        sizer_main.Add(self.panel_items, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        
        
        sizer_main.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        
        self.panel_bg.SetSizer(sizer_main)
        self.panel_bg.Layout()
        sizer_main.Fit(self.panel_bg)
        sizer_bg.Add(self.panel_bg, 1, wx.EXPAND, 5)
        
        
        self.SetSizer(sizer_bg)

        self.Maximize(maximised)

        self.Layout()

        self.setbinds()
        self.update_inventories(launch = True)
        self.Show()

    def setbinds(self):
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_IDLE, self._on_idle)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.tree_inventories.Bind(wx.EVT_TREE_SEL_CHANGED, 
                               self._on_inventory_selected)
        self.button_show_updated.Bind(wx.EVT_BUTTON, self._on_show_updated)

        for row in self.previews:
            for preview in row:
                preview["bitmap"].Bind(wx.EVT_ENTER_WINDOW,
                                       self._on_preview_mouseover)
                preview["bitmap"].Bind(wx.EVT_LEAVE_WINDOW,
                                       self._on_preview_mouseaway)

                preview["bitmap"].Bind(wx.EVT_RIGHT_DOWN,
                                       self._on_preview_rdown)
                preview["bitmap"].Bind(wx.EVT_RIGHT_UP,
                                       self._on_preview_rup)

    def _on_size(self, event):
        self._resized = True
        event.Skip()

    def _on_idle(self, event):
        if self._resized:
            self.Refresh()
            self._resized = False
        event.Skip()

    def _on_close(self, event):
        #Improvement: Previously, when closing the window, every tree item was
        # being selected under the current selection as part of closing the
        # window.  This caused it to take forever triggering
        # self._on_inventory_selected a bunch of times, taking up to about a
        # minute if the user has about 400 stash tabs.
        self.tree_inventories.Unbind(wx.EVT_TREE_SEL_CHANGED)

        x, y = self.GetPosition()
        w, h = self.GetSize()
        maximised = self.IsMaximized()
        self._app.mainframe_closed(x, y, w, h, maximised)
        event.Skip()

    def _on_inventory_selected(self, event):
        #<There must be a better way
        inventoryid = self.tree_inventories.GetSelection()
        label = self.tree_inventories.GetItemText(inventoryid)
        if not label.startswith("Inventory"):
            inventoryid = self.tree_inventories.GetItemParent(inventoryid)
            label = self.tree_inventories.GetItemText(inventoryid)
        index = int(label.split()[-1]) - 1
        #>

        self.clear_previews()

        x = 0
        y = 0
        for item in self.inventories[index]:
            preview = self.previews[x][y]
            preview["sizer"].StaticBox.SetLabel(item["_tab_label"] + " - " + item["name"])
            surf_preview = self.make_preview(item)
            img.show_pygame_surf_in_wxBitmap(surf_preview,
                                             preview["bitmap"])

            preview["bitmap"].item = item
            preview["bitmap"].surf = surf_preview

            x += 1
            if x == 6:
                x = 0
                y += 1

        self.Layout()
        self.Refresh()

    def update_inventories(self, launch = False):
        self.tree_inventories.DeleteChildren(self.tree_inventories.GetRootItem())
        self.clear_previews()

        if self._app.inventories:
            self._app.lock.acquire()
            self.inventories = self._app.inventories[:]
            self.items = self._app.items[:]
            self._app.lock.release()

            if launch:
                self._on_show_updated()
            else:
                self.button_show_updated.Show()

    def _on_show_updated(self, event = None):
        self.button_show_updated.Hide()

        self.cache_itempreviews = {}

        self.tree_inventories.inventoryids = []
        for i, inventory in enumerate(self.inventories, start = 1):
            _i = self.tree_inventories.AppendItem(self.tree_inventories.rootid,
                                                    "Inventory %s" % i)
            
            for item in inventory:
                self.tree_inventories.AppendItem(_i, item["name"] + " [" + item["_tab_label"] + "]")

        self.tree_inventories.ExpandAll()

        top = self.tree_inventories.GetFirstChild(self.tree_inventories.rootid)[0] #KEK
        #WHY DOES THAT RETURN TWO THINGS?  QUANTUM KEK

        self.tree_inventories.EnsureVisible(top)

    def make_preview(self, item):
        x, y, w, h = item["x"], item["y"], item["w"], item["h"]
        tab = item["_tab_label"]

        filtered = [i for i in self.items 
                    if (i.get("_socketed", False) == False) #ignore gems
                    and (i["inventoryId"] == item["inventoryId"])]

        positions = sorted([(i["x"], i["y"], i["w"], i["h"])
                            for i in filtered])
        old = self._tab_previews.get(tab, {"surf": grid.copy(),
                                           "positions": []})
        surf, oldpos = old["surf"], old["positions"]

        if oldpos != positions:
            for _item in filtered:
                _x, _y, _w, _h = _item["x"], _item["y"], _item["w"], _item["h"]
                this_is_it_yo = (_x, _y, _w, _h) == (x, y, w, h)
                _x *= 10
                _y *= 10

                _w *= 10
                _h *= 10
                _w -= 1
                _h -= 1

                itemblock = pygame.surface.Surface((_w, _h))
                itemblock.fill(uninterested)
                surf.blit(itemblock, (_x, _y))
                self._tab_previews[tab] = {"surf": surf, 
                                           "positions": positions}
        
        surf = surf.copy()

        itemblock = pygame.surface.Surface(((w * 10) - 1, (h * 10) - 1))
        itemblock.fill(interested)
        surf.blit(itemblock, (x * 10, y * 10))

        if item["name"] in self._ignored_items:
            pygame.draw.line(surf, 0xFF0000, (119, 0), (0, 119), 3)
            pygame.draw.line(surf, 0xFF0000, (119, 119), (0, 0), 3)

        return surf

    def clear_previews(self):
        self.Freeze()
        for col in self.previews:
            for preview in col:
                preview["sizer"].StaticBox.SetLabel(" ")
                img.show_pygame_surf_in_wxBitmap(grid, preview["bitmap"])
                preview["bitmap"].item = None
        self.Thaw()

    def _on_preview_mouseover(self, event):
        self.close_hoverpreview()

        item = event.GetEventObject().item
        if item:
            self._hoverpreview = ItemPreview(self, event.GetEventObject().item)

    def _on_preview_mouseaway(self, event):
        event.GetEventObject().right_down = False
        self.close_hoverpreview()

    def close_hoverpreview(self):
        if self._hoverpreview:
            self._hoverpreview.Destroy()
        self._hoverpreview = None

    def _on_preview_rdown(self, event):
        event.GetEventObject().right_down = True

    def _on_preview_rup(self, event):
        obj = event.GetEventObject()
        right_down = obj.right_down
        obj.right_down = False

        if right_down:
            self.toggle_ignore_preview(event.GetEventObject())

    def toggle_ignore_preview(self, preview):
        if preview.item:
            if preview.item["name"] in self._ignored_items:
                self.unignore_item(preview.item)
            else:
                self.ignore_item(preview.item)

    def unignore_item(self, item):
        self._ignored_items.remove(item["name"])

        for row in self.previews:
            for preview in row:
                if (preview["bitmap"].item) and (preview["bitmap"].item["name"] == item["name"]):

                    surf = self.make_preview(preview["bitmap"].item)
                    preview["bitmap"].surf = surf
                    img.show_pygame_surf_in_wxBitmap(surf, preview["bitmap"])

    def ignore_item(self, item):
        self._ignored_items.append(item["name"])

        for row in self.previews:
            for preview in row:
                if (preview["bitmap"].item) and (preview["bitmap"].item["name"] == item["name"]):

                    surf = preview["bitmap"].surf
                    pygame.draw.line(surf, 0xFF0000, (0, 119), (119, 0), 3)
                    pygame.draw.line(surf, 0xFF0000, (0, 0), (119, 119), 3)
                    img.show_pygame_surf_in_wxBitmap(surf, preview["bitmap"])
        
class ItemPreview(wx.Frame):
    def __init__(self, parent, item):
        wx.Frame.__init__(self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(-1,-1), style = wx.STAY_ON_TOP | wx.NO_BORDER | wx.TAB_TRAVERSAL)
        
        #This would work fine and look good if it wasn't for the fact that wx
        # is pants and won't let you load an external font file.  Pygame to the
        # rescue, ey chaps?
        """
        import ctypes
        _gdi32 = ctypes.WinDLL("gdi32.dll")
        _fonts = (font for font in os.listdir("font") 
                  if font.lower().endswith("ttf"))
        for font in _fonts:
            _gdi32.AddFontResourceA(os.path.join("font", font))

        _face = "Fontin-SmallCaps.ttf"
        self._font = wx.TheFontList.FindOrCreateFont(15, wx.FONTFAMILY_UNKNOWN,
                                                     wx.FONTSTYLE_NORMAL,
                                                     wx.FONTWEIGHT_NORMAL,
                                                     False, _face)
        
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        self.label_itemname = wx.StaticText(self, wx.ID_ANY, item["name"], wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_itemname.Wrap(-1)
        self.label_itemname.SetFont(self._font)
        self.label_itemname.SetForegroundColour(wx.Colour(254, 254, 118))
        
        sizer_main.Add(self.label_itemname, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.RIGHT | wx.LEFT, 5)
        
        self.label_itemtype = wx.StaticText(self, wx.ID_ANY, item["typeLine"], wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_itemtype.Wrap(-1)
        self.label_itemtype.SetFont(self._font)
        self.label_itemtype.SetForegroundColour(wx.Colour(254, 254, 118))
        
        sizer_main.Add(self.label_itemtype, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.RIGHT | wx.LEFT, 5)
        
        self.line_name_mods = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        sizer_main.Add(self.line_name_mods, 0, wx.EXPAND | wx.ALL, 5)
        
        for mod in item["explicitMods"]:
            label = wx.StaticText(self, wx.ID_ANY, mod)
            label.SetFont(self._font)
            label.SetForegroundColour(wx.Colour(135, 135, 254))

            sizer_main.Add(label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.RIGHT | wx.LEFT, 5)

        """#
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.Colour(0, 0, 0))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)

        self.bitmap_preview = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0)
        sizer_main.Add(self.bitmap_preview, 0, wx.ALL, 5)

        if item in [json.loads(cached_item) for cached_item
                    in self.Parent.cache_itempreviews]:
            keys = self.Parent.cache_itempreviews.keys()
            decoded = [json.loads(key) for key in keys]
            i = decoded.index(item)

            preview = self.Parent.cache_itempreviews[keys[i]]
        else:
            preview = make_itempreview(item)

        img.show_pygame_surf_in_wxBitmap(preview, 
                                         self.bitmap_preview)

        self.Parent.cache_itempreviews[json.dumps(item)] = preview

        """#"""
        
        self.SetSizer(sizer_main)
        self.Layout()
        sizer_main.Fit(self)

        self.tick = wx.Timer()
        self.tick.Start(1 / 60.0)

        self.setbinds()

        self._set_position()

        self.Disable()
        self.Show()

    def setbinds(self):
        self.tick.Bind(wx.EVT_TIMER, self._on_tick)

    def _on_tick(self, event):
        self._set_position()

    def _set_position(self):
        pad = 20

        m_x, m_y = wx.GetMousePosition()
        s_x, s_y = self.GetSize()

        l = m_x - s_x - pad
        r = m_x + pad
        u = m_y - s_y - pad
        d = m_y + pad

        upperright = (r, u)
        upperleft = (l, u)
        bottomright = (r, d)
        bottomleft = (l, d)

        positions = (upperright,
            upperleft,
            bottomright,
            bottomleft,)

        area = wx.Display(wx.Display_GetFromPoint((m_x, m_y))).GetClientArea()

        for pos in positions:
            if area.ContainsRect(wx.Rect(pos[0], pos[1], s_x, s_y)):
                break

        self.SetPosition(pos) #leftover from for loop

def test():
    t = None
    if t == "ItemPreview":
        import wx
        a = wx.App()
        class _(wx.Frame):
            pass
        parent = _(None)
        parent.cache_itempreviews = {}
        p = ItemPreview(parent, {u'socketedItems': [], u'corrupted': False, 'links': 'G-R-R-R R', u'typeLine': u'Highland Blade', u'implicitMods': [u'18% increased Accuracy Rating'], u'flavourText': [u'"Today, clansmen, my sword is my voice!"\r', u'- Rigvald, at the Battle of Glarryn'], u'sockets': [{u'group': 0, u'attr': u'D'}, {u'group': 0, u'attr': u'S'}, {u'group': 0, u'attr': u'S'}, {u'group': 0, u'attr': u'S'}, {u'group': 1, u'attr': u'S'}], u'lockedToCharacter': False, u'verified': False, u'support': True, u'frameType': 3, u'explicitMods': [u'147% increased Physical Damage', u'20% increased Attack Speed', u'+154 to Accuracy Rating', u'10% increased Movement Speed'], u'_type': 0, u'_socketed': False, u'inventoryId': u'Stash11', u'requirements': [{u'displayMode': 0, u'values': [[u'44', 0]], u'name': u'Level'}, {u'displayMode': 1, u'values': [[u'77', 0]], u'name': u'Str'}, {u'displayMode': 1, u'values': [[u'77', 0]], u'name': u'Dex'}], u'properties': [{u'displayMode': 0, u'values': [], u'name': u'Two Handed Sword'}, {u'displayMode': 0, u'values': [[u'+20%', 1]], u'name': u'Quality'}, {u'displayMode': 0, u'values': [[u'115-214', 1]], u'name': u'Physical Damage'}, {u'displayMode': 0, u'values': [[u'5.00%', 0]], u'name': u'Critical Strike Chance'}, {u'displayMode': 0, u'values': [[u'1.50', 1]], u'name': u'Attacks per Second'}], u'icon': u'https://p7p4m6s5.ssl.hwcdn.net/image/Art/2DItems/Weapons/TwoHandWeapons/TwoHandSwords/TwoHandSword5Unique.png?scale=1&w=2&h=4&v=fb4f93392d82b1f9d21f9fa6236ac54f3', u'league': u'Hardcore', u'name': u"Rigvald's Charge", u'_tab': 10, u'h': 4, u'identified': True, 'rarity': 'Unique', u'w': 2, u'_tab_label': u'*', u'y': 3, u'x': 2})
        a.MainLoop()