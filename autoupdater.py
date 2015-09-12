import time
import json
import urllib2
import threading

import version

class Updater(threading.Thread):
    def __init__(self, app, callback, githubuser, repo, branch = "master"):
        super(Updater, self).__init__()
        self.callback = callback
        self._app = app
        self.user = githubuser
        self.repo = repo
        self.branch = branch
        self.version = json.loads(version.version)
        self.patch_notes = ""
        self._next_check = 15
        self.remote_version = [0]

    def run(self):
        while self._app.alive:
            if self._next_check <= 0: #<= instead of == saves locking
                if self.update_available():
                    self.callback(self.version,
                                  self.remote_version,
                                  self.patch_notes)
                self._next_check = 60*60*5
            else:
                self._next_check -= 1

            time.sleep(1)

    def _get_github_stub(self):
        skele = "https://raw.githubusercontent.com/%s/%s/%s/"
        url = skele % (self.user, self.repo, self.branch)
        return url

    def _get_github_file(self, fname, readlines = False):
        url = self._get_github_stub() + fname
        try:
            res = urllib2.urlopen(url)
        except urllib2.HTTPError:
            return [] if readlines else ""

        if readlines:
            remote = res.readlines()
        else:
            remote = res.read()
        
        return remote

    def get_remote_version(self):
        remote = self._get_github_file("version.py", readlines = True)
        remote = [line.strip() for line in remote]
        version = [line for line in remote if line.startswith("version")]
        if not version:
            #All version tuples are greater than this, therefore an update is
            # not available or unavailable
            return 0

        version = json.loads(version[0].split("=")[-1].strip("\" "))
        return version

    def update_patch_notes(self):
        self.patch_notes = self._get_github_file("Patch Notes.txt")

    def update_available(self):
        self.remote_version = self.get_remote_version()
        if self.remote_version > self.version:
            self.update_patch_notes()
            return True
        else:
            return False

    def ignore_remote_version(self):
        self.version = self.get_remote_version()

    def check_now(self):
        self._next_check = 0

def update(updater_instance, pid, restart_file):
    with file("__patch notes.tmp", "w") as f:
        f.write(updater_instance.patch_notes)

    zip_skele = "https://github.com/%s/%s/archive/%s.zip"
    zip = zip_skele % (
        updater_instance.user,
        updater_instance.repo,
        updater_instance.branch)

    args = (pid, "__patch notes.tmp", zip, restart_file)
    out = []
    for arg in args:
        str_arg = str(arg)
        escaped = str_arg.replace("\"","\\\"")
        enclosed = "\"" + escaped + "\""
        out.append(enclosed)
    
    args = " ".join(out)

    os.system("start upgrade.py" + " " + args)