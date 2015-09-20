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
            j = read_item_db(os.path.join(datadir, path))
            j = [x["league"] for x in j
                 if ("league" in x.keys())]
            l = set(j)
            leagues.extend(l)
        except:
            pass
    return leagues

def get_path_by_league(league):
    for path in os.listdir(datadir):
        try:
            j = read_item_db(os.path.join(datadir, path))
            for item in j:
                if item.has_key("league"):
                    if item["league"] == league:
                        return path
        except:
            pass
    return False

def read_item_db(path):
    try:
        d = sqlite3.connect(path)
        c = d.execute("SELECT value FROM data WHERE key = 'items'")
        r = c.fetchone()
        j = json.loads(str(r[0]))
    except:
        return False
    return j

def get_items(fpaths_db, stash_tabs):
    stash_tabs = [unicode(stash_tab) for stash_tab in stash_tabs]
    for path in fpaths_db:
        try:
            j = read_item_db(os.path.join(datadir, path))
            j = [x for x in j
                    if ("name" in x.keys())
                    and ("_tab_label" in x.keys())
                    and (x["_tab_label"] in stash_tabs)]
            assert len(j) > 0
            break
        except:
            pass
    else: #nobreak
        return Result(False)

    for item in j:
        item["name"] = item["name"].rsplit(">")[-1]

    return Result(True,
                  items = j, 
                  mtime = os.path.getmtime(path),
                  fname = os.path.split(path)[-1],
                  league = j[0]["league"])
