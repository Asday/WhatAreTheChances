import os
import sys
import threading
import json
import time

import wx

import interface
import config
import autoupdater
import acquisition

class SettingsWatcher(threading.Thread):
    #I'm lead to believe reading from a dict is threadsafe.  This class hinges
    # on that.  RIP on in fluffy memories, sweet meme-artist.
    def __init__(self, app):
        super(SettingsWatcher, self).__init__()
        self._app = app
        self.update_copy()
        self.check_interval = 15
        self.next_check = 15

    def update_copy(self):
        self._last_settings = self._app.settings.copy()

    def run(self):
        while self._app.alive:
            if self.next_check <= 0:
                if not self._app.settings == self._last_settings:
                    self._app.write_settings()
                    self.update_copy()
                self.next_check = self.check_interval
            else:
                self.next_check -= 1

            time.sleep(1)

def subdivide_recipes(itemlist):
    itemlist = itemlist[:]
    out = []
    while itemlist:
        recipe = []
        item = itemlist.pop(0)
        recipe.append(item)
        while itemlist:
            if itemlist[0]["name"] == recipe[0]["name"]:
                item = itemlist.pop(0)
                recipe.append(item)
            else:
                break
        out.append(recipe)
    return out

def key_sort_recipe_by_tab(recipe):
    return min([item["_tab_label"] for item in recipe])

def fill_inventories(recipes):
    out = []
    i = Inventory()

    inventory = []
    for recipe in recipes:
        fits = True
        for item in recipe:
            #check to see that the whole recipe fits
            if not i.place(item):
                fits = False
                #if it doesn't, get outta here
                break

        if not fits:
            #If it doesn't, it's 'cause the inventory got too full
            # chunk that inventory to the output, make a new one, and carry on
            inventory.sort(key = _tabname)
            out.append(inventory)
            inventory = []
            i.clear()
        
        for item in recipe:
            #add every item to the inventory
            if not fits:
                #Make sure the inventory actually accounts for them if we just
                # cleared it.  BUGFIX
                i.place(item)
            inventory.append(item)

    if inventory:
        #Bug found by @WrKnght; if you didn't have a full inventory of stuff
        # WhatAreTheChances pretended you didn't have SHIT D:
        out.append(inventory)

    return out

def _tabname(item):
    try:
        i = str(int(item["_tab_label"])).zfill(3)
    except ValueError:
        i = item["_tab_label"]

    return i

def inventorysort(itemlist):
    recipes = subdivide_recipes(itemlist)
    recipes.sort(key = key_sort_recipe_by_tab)
    inventories = fill_inventories(recipes)

    return inventories

def _nameorder(item):
    return item["name"]

def chancerecipes(items):
    #Get a count of each name in unignored stash tabs
    names = [item["name"]
                for item 
                in items]

    counts = [names.count(name) for name in names]

    for i, count in enumerate(counts):
        items[i]["count"] = count

    chances = [item
               for item
               in items
               if item["count"] == 2]
    alchs = [item
             for item
             in items
             if item["count"] == 3]
    chances.extend([item
                    for item
                    in items
                    if item["count"] == 4])

    chances.sort(key = _nameorder)
    alchs.sort(key = _nameorder)

    recipes = alchs + chances

    return inventorysort(recipes)

class Inventory(object):
    def __init__(self):
        self.clear()

    def place(self, item):
        if item["h"] == 4: #Place from topright
            for x in xrange(11, -1, -1):
                if self._is_open(item, (x, 0)):
                    self._place(item, (x, 0))
                    return True
        elif item["h"] == 3: #Place from topleft
            for x in range(12):
                if self._is_open(item, (x, 0)):
                    self._place(item, (x, 0))
                    return True
        elif item["h"] == 2: #Place from bottomleft
            for x in range(12):
                if self._is_open(item, (x, 3)):
                    self._place(item, (x, 3))
                    return True
        elif item["h"] == 1: #Place from one above bottomleft, then bottomleft
                             # then rightwards from there in columns
            for x in range(12):
                if self._is_open(item, (x, 3)):
                    self._place(item, (x, 3))
                    return True
                elif self._is_open(item, (x, 4)):
                    self._place(item, (x, 4))
                    return True
        
        return False

    def clear(self):
        self._inventory = [[False for _ in range(5)] for _ in range(12)]

    def _is_open(self, item, topleft):
        x, y = topleft
        for item_x in xrange(item["w"]):
            for item_y in xrange(item["h"]):
                try:
                    if self._inventory[x + item_x][y + item_y]:
                        return False
                except IndexError:
                    return False

        return True

    def _place(self, item, topleft):
        x, y = topleft
        for item_x in xrange(item["w"]):
            for item_y in xrange(item["h"]):
                self._inventory[x + item_x][y + item_y] = True

class AcquisitionThread(threading.Thread):
    def __init__(self, app, league):
        super(AcquisitionThread, self).__init__()
        self._app = app

    def run(self):
        while self._app.alive:
            if self._app.last_update_touched:
                self._app.last_update_touched = False

            if "league" in self._app.settings:
                league = self._app.settings["league"]
            else:
                league = None

            tabs = self._app.settings["stash_tabs"]
            filter_tabs = self._app.settings.get("stash_tabs_filter", True)

            res = acquisition.get_items(
                acquisition.get_probable_fpaths(league),
                tabs, filter_tabs)

            if not (res.success and res.mtime > self._app.last_update):
                time.sleep(config.sleepytime)
                continue

            items = res.items
            mtime = res.mtime
            fname = res.fname

            inventories = chancerecipes(items)
            
            #Notify the user?
            new = inventories
            if self._app.inventories:
                old = self._app.inventories
            else:
                old = []
            newnames = sum([[item["name"]
                             for item 
                             in inventory]
                            for inventory in new],
                           [])
            oldnames = sum([[item["name"]
                             for item
                             in inventory]
                            for inventory
                            in old],
                           [])

            newnames.sort()
            oldnames.sort()

            new_recipes = [] #If this gets filled, they'll be notified

            #If there are new recipes
            if len(new) != len(old) or newnames != oldnames:
                #Get a list of the new stuff
                newstuff = set()
                for name in newnames:
                    if name in oldnames:
                        oldnames.remove(name)
                    else:
                        newstuff.add(name)

                for name in newstuff:
                    recipe = []
                    for item in sum(new, []): #unpack the inventories
                        if item["name"] == name:
                            recipe.append(item)
                    new_recipes.append(recipe)

            #sort the recipes properly
            for inventory in inventories:
                inventory.sort(key = lambda item: item["_tab_label"].zfill(3))

            #update app's recipe list
            self._app.lock.acquire()
            self._app.inventories = inventories
            self._app.items = items
            self._app.lock.release()
            self._app.inventories_updated(new_recipes)

            self._app.current_file = fname
            #While we were looping, something else may have updated this value,
            # so we need to heed the value it currently has on the next
            # iteration, hence, we only update the value ourselves if nothing
            # else has.
            if not self._app.last_update_touched:
                self._app.last_update = mtime

            time.sleep(config.sleepytime)

class App(wx.App):
    def __init__(self):
        super(App, self).__init__()

        try:
            with file("settings.cfg", "r") as f:
                self.settings = json.load(f)
                if not isinstance(self.settings, dict):
                    self.settings = {"stash_tabs": []}
        except IOError:
            self.settings = {"stash_tabs": []}

        self._trayicon = interface.trayicon.Main(self)
        self._mainframe = None
        self._updateframe = None
        self._settingsframe = None

        self.lock = threading.Lock()
        self.inventories = None
        self.items = None
        self.alive = True
        self.last_update = 0
        self.last_update_touched = False
        self.ignored_files = []

        league = self.settings["league"] if "league" in self.settings else None
        self._acqthread = AcquisitionThread(self, league)
        self._updater = autoupdater.Updater(self, self._update_available,
                                            "Asday", "WhatAreTheChances")
        self._settingswatcher = SettingsWatcher(self)

        self.update_available = False

        self._acqthread.start()
        self._updater.start()
        self._settingswatcher.start()
        
        if not self.settings["stash_tabs"]:
            wx.CallAfter(self.launch_settings_window)

        self.MainLoop()

        self.alive = False

        #Need to join the settingswatcher before we perform the final settings
        # write
        self._settingswatcher.join()

        self.write_settings()

        self._acqthread.join()
        self._updater.join()

    def write_settings(self):
        try:
            with file("settings.cfg", "w") as f:
                json.dump(self.settings, f)
        except IOError:
            pass

    def launch_mainframe(self):
        #Load window position
        try:
            x = self.settings["main_x"]
            y = self.settings["main_y"]
            w = self.settings["main_w"]
            h = self.settings["main_h"]
            position = (x, y)
            size = (w, h)
        except KeyError:
            position = wx.DefaultPosition
            size = (1280, 720)

        if not self._mainframe:
            self._mainframe = interface.mainframe.Main(self, position, size)
        style = self._mainframe.GetWindowStyle()
        self._mainframe.SetWindowStyle(style | wx.STAY_ON_TOP)
        self._mainframe.Raise()
        self._mainframe.SetWindowStyle(style)

    def mainframe_closed(self, x, y, w, h):
        self.settings.update(
            {"main_x": x,
             "main_y": y,
             "main_w": w,
             "main_h": h}
            )

        self._mainframe = None

    def launch_update_window(self):
        try:
            x = self.settings["update_x"]
            y = self.settings["update_y"]
            w = self.settings["update_w"]
            h = self.settings["update_h"]
            position = (x, y)
            size = (w, h)
        except KeyError:
            position = wx.DefaultPosition
            size = (610, 537)

        self._updateframe = interface.update.Main(self, self.local_version,
                                                  self.remote_version,
                                                  self.patch_notes,
                                                  position, size)

    def update_window_closed(self, x, y, w, h):
        self.settings.update(
            {"update_x": x,
             "update_y": y,
             "update_w": w,
             "update_h": h}
            )

        self._updateframe = None

    def launch_settings_window(self):
        if not self._settingsframe:
            self._settingsframe = interface.settings.Main(
                self, self.get_current_league())
        style = self._settingsframe.GetWindowStyle()
        self._settingsframe.SetWindowStyle(style | wx.STAY_ON_TOP)
        self._settingsframe.Raise()
        self._settingsframe.SetWindowStyle(style)

    def get_current_league(self):
        return self.settings["league"] if "league" in self.settings else None

    def settings_window_closed(self):
        self._settingsframe = None

    def check_for_updates(self):
        self._updater.check_now()

    def _update_available(self, local_version, remote_version, patch_notes):
        self.update_available = True
        self.local_version = local_version
        self.remote_version = remote_version
        self.patch_notes = patch_notes
        self._trayicon.update_available()

    def inventories_updated(self, new_recipes):
        if self._mainframe:
            wx.CallAfter(self._mainframe.update_inventories)

        if new_recipes:
            wx.CallAfter(self._trayicon.new_recipes, new_recipes)

    def ignore_update(self):
        self._updater.ignore_remote_version()
        self.update_available = False

    def update(self):
        autoupdater.update(self._updater, os.getpid(), sys.argv[0])
        self.quit()

    def recheck_items(self):
        self.last_update_touched = True
        self.last_update = 0

    def quit(self):
        self._trayicon.RemoveIcon()
        try:
            self._mainframe.Hide()
        except AttributeError:
            pass

        try:
            self._updateframe.Hide()
        except AttributeError:
            pass

        try:
            self._settingsframe.Hide()
        except AttributeError:
            pass

        wx.Exit()

App()
