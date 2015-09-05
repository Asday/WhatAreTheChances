import time
import json
import requests
import threading

import version

class Updater(threading.Thread):
    def __init__(self, app, callback, githubuser, repo, branch = "master"):
        super(Updater, self).__init__()
        self.callback = callback
        self._app = app
        self._user = githubuser
        self._repo = repo
        self._branch = branch
        self.version = json.loads(version.version)
        self.patch_notes = ""
        self._next_check = 3
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
        url = skele % (self._user, self._repo, self._branch)
        return url

    def _get_github_file(self, fname, readlines = False):
        url = self._get_github_stub() + fname
        res = requests.get(url)
        if res.status_code != 200:
            return [] if readlines else ""

        if readlines:
            remote = res.text.split("\n")
        else:
            remote = res.text
        
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