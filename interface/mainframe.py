import json

import wx
import pygame
import pygame.gfxdraw

import img

grid = pygame.surface.Surface((119, 119))
grid.fill(0x000000)
gridcolour = pygame.color.Color(104, 104, 104)
interested = pygame.color.Color(255, 126, 44)
uninterested = pygame.color.Color(64, 30, 26)
for offset in xrange(10, 119, 10):
    pygame.gfxdraw.line(grid, offset - 1, 0, offset - 1, 119, gridcolour)
    pygame.gfxdraw.line(grid, 0, offset - 1, 119, offset - 1, gridcolour)
    if offset % 20 == 0:
        pygame.gfxdraw.line(grid, offset, 0, offset, 119, gridcolour)
    if offset % 60 == 0:
        pygame.gfxdraw.line(grid, 0, offset, 119, offset, gridcolour)

class Main(wx.Frame):
    def __init__(self, app, position, size):
        self._app = app
        self._tab_previews = {}

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
                preview["sizer"].Add(panel, 1, wx.EXPAND | wx.ALL, 5)
                grid_items.Add(preview["sizer"], 0, 0, 5)
                
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
        self.Layout()

        self.setbinds()
        self.update_inventories()
        self.Show()

    def setbinds(self):
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.tree_inventories.Bind(wx.EVT_TREE_SEL_CHANGED, 
                               self._on_inventory_selected)

    def _on_close(self, event):
        x, y = self.GetPosition()
        w, h = self.GetSize()
        self._app.mainframe_closed(x, y, w, h)
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
            preview["sizer"].StaticBox.SetLabel(
                item["_tab_label"] + " - " + item["name"])
            surf_preview = self.make_preview(item)
            img.show_pygame_surf_in_wxBitmap(surf_preview,
                                                preview["bitmap"])

            x += 1
            if x == 6:
                x = 0
                y += 1

    def update_inventories(self):
        self.tree_inventories.DeleteChildren(
            self.tree_inventories.GetRootItem())
        self.clear_previews()

        if self._app.inventories:
            self._app.lock.acquire()
            self.inventories = self._app.inventories[:]
            self.items = self._app.items[:]
            self._app.lock.release()

            self.tree_inventories.inventoryids = []
            for i, inventory in enumerate(self.inventories, start = 1):
                _i = self.tree_inventories.AppendItem(self.tree_inventories.rootid,
                                                      "Inventory %s" % i)
            
                for item in inventory:
                    self.tree_inventories.AppendItem(_i, item["name"] + " [" + item["_tab_label"] + "]")

            self.tree_inventories.ExpandAll()

            top = self.tree_inventories.GetFirstChild(
                self.tree_inventories.rootid)[0] #KEK
            #WHY DOES THAT RETURN TWO THINGS?  QUANTUM KEK

            self.tree_inventories.EnsureVisible(top)

    def make_preview(self, item):
        x, y, w, h = item["x"], item["y"], item["w"], item["h"]
        tab = item["_tab_label"]

        filtered = [i for i in self.items 
                    if i["_tab_label"] == tab
                    and (i.get("_socketed", False) == False)]

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

        return surf

    def clear_previews(self):
        self.Freeze()
        for col in self.previews:
            for preview in col:
                preview["sizer"].StaticBox.SetLabel(" ")
                img.show_pygame_surf_in_wxBitmap(grid, preview["bitmap"])
        self.Thaw()
        
