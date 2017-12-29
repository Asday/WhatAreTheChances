import os
import json
import sqlite3
from collections import defaultdict

from result import Result

if os.name == "nt":
    datadir = os.path.join(os.path.expanduser("~"), 
                            r"AppData\Local\acquisition\data")
elif os.name == "posix":
    datadir = "~/.local/share/acquisition/data"

rarities = {
    0: "Normal",
    1: "Magic",
    2: "Rare",
    3: "Unique",
    4: "Gem",
    5: "Currency",
    6: "Card",
    8: "Prophecy",
    9: "Relic",
    }
rarities = defaultdict(lambda: "fuck knows", **rarities)

attr_to_col = {
    "G": "W",
    "S": "R",
    "I": "B",
    "D": "G",
    False: "W",
    }

_cache_leagues = {}

def clear_cache():
    global _cache_leagues
    _cache_leagues = {}

def get_leagues():
    leagues = []
    for path in os.listdir(datadir):
        try:
            _json = read_item_db(os.path.join(datadir, path))
            filtered = [item["league"] for item in _json
                        if ("league" in item.keys())]
            _leagues = set(filtered)
            leagues.extend(_leagues)
        except:
            pass
    return leagues

def get_fname_by_league(league):
    if league in _cache_leagues:
        #Bug?  If the file is renamed, the cache is invalidated and a restart
        # is needed.  Is that even a big deal?  KEK
        return _cache_leagues[league]

    if not league: #Uninitialised settings, get most recently modified
        lstdir = os.listdir(datadir)
        lstdir.sort(key = lambda x: os.path.getmtime(os.path.join(datadir, x)))
        return lstdir[-1]

    for path in os.listdir(datadir):
        try:
            _json = read_item_db(os.path.join(datadir, path))
            for item in _json:
                if item.has_key("league"):
                    if item["league"] == league:
                        _cache_leagues[league] = path
                        return path
                    else:
                        break
        except:
            pass
    return False

def read_item_db(path):
    try:
        db = sqlite3.connect(path)
        cursor = db.execute("SELECT value FROM data WHERE key = 'items'")
        row = cursor.fetchone()
        _json = json.loads(str(row[0]))
    except:
        return False
    return _json

def get_items(league, stash_tabs = None, filter_tabs = False):
    stash_tabs = [] if stash_tabs == None else stash_tabs
    stash_tabs = [unicode(stash_tab) for stash_tab in stash_tabs]

    path = get_fname_by_league(league)
    
    try:
        _json = read_item_db(os.path.join(datadir, path))

        _json = [val for val in _json
                    if ("name" in val.keys())
                    and ("_tab_label" in val.keys())]

        if filter_tabs:
            _json = [item for item in _json
                        if item["_tab_label"] in stash_tabs]

        assert len(_json) > 0
    except BaseException as e:
        print(e)
        return Result(False)
    

    for item in _json:
        item["name"] = item["name"].rsplit(">")[-1]
        item["typeLine"] = item["typeLine"].rsplit(">")[-1]
        if "frameType" in item:
            item["rarity"] = rarities[item["frameType"]]

        if item.has_key("sockets"):
            group = None
            links = []
            for socket in item["sockets"]:
                if socket["group"] == group:
                    links.append("-")
                else:
                    links.append(" ")
                links.append(attr_to_col[socket["attr"]])
                group = socket["group"]

            links = "".join(links)[1:]

            item["links"] = links

    return Result(True,
                  items = _json, 
                  fname = os.path.split(path)[-1],
                  league = _json[0]["league"])

def get_mtime(league):
    fname = get_fname_by_league(league)
    if fname:
        return os.path.getmtime(os.path.join(datadir, fname))
    
    return False