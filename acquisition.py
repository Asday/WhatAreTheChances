import os
import json
import sqlite3

from result import Result

if os.name == "nt":
    datadir = os.path.join(os.path.expanduser("~"), 
                            r"AppData\Local\acquisition\data")
elif os.name == "posix":
    datadir = "~/.local/share/acquisition/data"

def get_probable_fpaths(league):
    def mtime(x):
        return os.path.getmtime(os.path.join(datadir, x))

    path = None
    if league:
        path = get_path_by_league(league)
        if path:
            listdir = [path]
    
    if not path:
        listdir = os.listdir(datadir)

    probably = sorted(listdir, key = mtime)

    return (os.path.join(datadir, fpath) for fpath in probably)

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

def get_path_by_league(league):
    for path in os.listdir(datadir):
        try:
            _json = read_item_db(os.path.join(datadir, path))
            for item in _json:
                if item.has_key("league"):
                    if item["league"] == league:
                        return path
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

def get_items(fpaths_db, stash_tabs = None, filter_tabs = True):
    stash_tabs = [] if stash_tabs == None else stash_tabs
    stash_tabs = [unicode(stash_tab) for stash_tab in stash_tabs]
    for path in fpaths_db:
        try:
            _json = read_item_db(os.path.join(datadir, path))

            _json = [val for val in _json
                     if ("name" in val.keys())
                     and ("_tab_label" in val.keys())]

            if filter_tabs:
                _json = [item for item in _json
                         if item["_tab_label"] in stash_tabs]

            assert len(_json) > 0
            break
        except:
            pass
    else: #nobreak
        return Result(False)

    for item in _json:
        item["name"] = item["name"].rsplit(">")[-1]

    return Result(True,
                  items = _json, 
                  mtime = os.path.getmtime(path),
                  fname = os.path.split(path)[-1],
                  league = _json[0]["league"])
