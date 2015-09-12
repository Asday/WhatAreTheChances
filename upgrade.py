import os
import sys
import threading
import time
import shutil
import urllib2
import zipfile

import wx
import wx.lib.newevent

def download_with_progress(url, filelike, report_hook = None):
    bytes_so_far = 0
    response = urllib2.urlopen(url)

    while True:
        chunk = response.read(1024)
        bytes_so_far += len(chunk)

        if not chunk:
            break
        else:
            filelike.write(chunk)

        if report_hook:
            report_hook(bytes_so_far)

if os.name == "nt":
    def pid_is_running(pid):
        #credit: http://stackoverflow.com/a/28065945/1149933
        import ctypes
        desired_access = 0x1000 #PROCESS_QUERY_LIMITED_INFORMATION
        inherit_handle = False
        hnd = ctypes.windll.kernel32.OpenProcess(desired_access, 
                                                 inherit_handle,
                                                 pid)
        if hnd:
            ctypes.windll.kernel32.CloseHandle(hnd)
            return True
        else:
            return False
elif os.name == "posix":
    def pid_is_running(pid):
        #untested, whatever
        try:
            os.kill(pid, 0)
            return True
        except:
            return False


def humanise_filesize(bytes):
    if 0 <= bytes < 1024:
        return "%s B" % bytes
    elif 1024 <= bytes < 1024**2:
        return "%0.2f KiB" % (bytes / 1024.0)
    elif 1024**2 <= bytes < 1024**3:
        return "%0.2f MiB" % (bytes / 1024.0**2)
    elif 1024**3 <= bytes < 1024**4:
        return "%0.2f GiB" % (bytes / 1024.0**3)
    elif 1024**4 <= bytes:
        return "%0.2f TiB" % (bytes / 1024.0**4)
    else: #negative
        return "pretty fuckin' small yo"

class Downloader(threading.Thread):
    def __init__(self, frame, url, evt_poke, evt_complete):
        super(Downloader, self).__init__()
        self.frame = frame
        self.url = url
        self.evt_poke = evt_poke
        self.evt_complete = evt_complete

    def run(self):
        with file("__patch.zip", "wb") as f:
            download_with_progress(self.url, f, self._poke)
        wx.PostEvent(self.frame, self.evt_complete())

    def _poke(self, bytes):
        self.evt_poke.data = bytes
        wx.PostEvent(self.frame, self.evt_poke(data = bytes))

class Waiter(threading.Thread):
    def __init__(self, frame, pid, evt_complete):
        super(Waiter, self).__init__()
        self.frame = frame
        self.pid = pid
        self.evt_complete = evt_complete

    def run(self):
        while pid_is_running(self.pid):
            time.sleep(1)

        wx.PostEvent(self.frame, self.evt_complete())

class Extractor(threading.Thread):
    def __init__(self, frame, evt_complete):
        super(Extractor, self).__init__()
        self.frame = frame
        self.evt_complete = evt_complete

    def run(self):
        zip = zipfile.ZipFile("__patch.zip")
        try:
            os.mkdir("__patch")
        except WindowsError as e:
            if e.errno == 17: #already exists
                pass

        zip.extractall("__patch")
        zip.close()

        folder = os.listdir("__patch")[0]
        for fname in os.listdir(os.path.join("__patch", folder)):
            try:
                os.remove(fname)
            except:
                pass
            shutil.move(os.path.join("__patch", folder, fname), fname)

        wx.PostEvent(self.frame, self.evt_complete())

class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent = None, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size(500,300), style = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        
        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        
        sizer_bg = wx.BoxSizer(wx.VERTICAL)
        
        self.panel_bg = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.panel_bg.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU))
        
        sizer_main = wx.BoxSizer(wx.VERTICAL)
        
        self.listbook_stage = wx.Listbook(self.panel_bg, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT)
        self.panel_downloading = wx.Panel(self.listbook_stage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizer_downloading = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_downloading.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.label_downloading = wx.StaticText(self.panel_downloading, wx.ID_ANY, u"Fetching %s...", wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_downloading.Wrap(-1)
        sizer_downloading.Add(self.label_downloading, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        self.label_downloaded = wx.StaticText(self.panel_downloading, wx.ID_ANY, u"", wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_downloaded.skele = u"%s downloaded..."
        self.label_downloaded.Wrap(-1)
        sizer_downloading.Add(self.label_downloaded, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_downloading.AddSpacer((0, 0), 2, wx.EXPAND, 5)
        
        
        self.panel_downloading.SetSizer(sizer_downloading)
        self.panel_downloading.Layout()
        sizer_downloading.Fit(self.panel_downloading)
        self.listbook_stage.AddPage(self.panel_downloading, u"Downloading", True)
        self.panel_waiting = wx.Panel(self.listbook_stage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizer_waiting = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_waiting.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.label_waiting = wx.StaticText(self.panel_waiting, wx.ID_ANY, u"Waiting for %s to close.  If this hasn't happened with some manner of rapidity, do please open the task manager and kill it yourself.  The PID should be %s.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_waiting.Wrap(250)
        sizer_waiting.Add(self.label_waiting, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_waiting.AddSpacer((0, 0), 2, wx.EXPAND, 5)
        
        
        self.panel_waiting.SetSizer(sizer_waiting)
        self.panel_waiting.Layout()
        sizer_waiting.Fit(self.panel_waiting)
        self.listbook_stage.AddPage(self.panel_waiting, u"Waiting", False)
        self.panel_extracting = wx.Panel(self.listbook_stage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizer_extracting = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_extracting.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.label_extracting = wx.StaticText(self.panel_extracting, wx.ID_ANY, u"Currently extracting %s, (%s/%s)...", wx.DefaultPosition, wx.DefaultSize, 0)
        self.label_extracting.Wrap(-1)
        sizer_extracting.Add(self.label_extracting, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        self.progress_extracting = wx.Gauge(self.panel_extracting, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL)
        self.progress_extracting.SetValue(0) 
        sizer_extracting.Add(self.progress_extracting, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_extracting.AddSpacer((0, 0), 2, wx.EXPAND, 5)
        
        
        self.panel_extracting.SetSizer(sizer_extracting)
        self.panel_extracting.Layout()
        sizer_extracting.Fit(self.panel_extracting)
        self.listbook_stage.AddPage(self.panel_extracting, u"Extracting", False)
        self.panel_finished = wx.Panel(self.listbook_stage, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sizer_finished = wx.BoxSizer(wx.VERTICAL)
        
        
        sizer_finished.AddSpacer((0, 0), 1, wx.EXPAND, 5)
        
        self.static_finished = wx.StaticText(self.panel_finished, wx.ID_ANY, u"Finished updating the program for you.  It will relaunch automatically in a few seconds.  Cheers for waiting.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.static_finished.Wrap(250)
        sizer_finished.Add(self.static_finished, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        
        
        sizer_finished.AddSpacer((0, 0), 2, wx.EXPAND, 5)
        
        
        self.panel_finished.SetSizer(sizer_finished)
        self.panel_finished.Layout()
        sizer_finished.Fit(self.panel_finished)
        self.listbook_stage.AddPage(self.panel_finished, u"Finished", False)
        
        sizer_main.Add(self.listbook_stage, 1, wx.EXPAND | wx.ALL, 5)
        
        
        self.panel_bg.SetSizer(sizer_main)
        self.panel_bg.Layout()
        sizer_main.Fit(self.panel_bg)
        sizer_bg.Add(self.panel_bg, 1, wx.EXPAND, 5)
        
        
        self.SetSizer(sizer_bg)
        self.Layout()

        self.Show()

        (self.pid, patch_notes_file,
         remote_resource, self.restart_file) = sys.argv[1:]

        with file(patch_notes_file, "r") as f:
            patch_notes = f.read()

        os.remove(patch_notes_file)

        downloader_poke, evt_downloader_poke = wx.lib.newevent.NewEvent()
        downloader_complete, evt_downloader_complete = wx.lib.newevent.NewEvent()

        self.Bind(evt_downloader_poke, self.update_download_progress)
        self.Bind(evt_downloader_complete, self.wait_on_pid)
        
        downloader = Downloader(self, remote_resource,
                                downloader_poke,
                                downloader_complete)

        downloader.start()


    def update_download_progress(self, event):
        wx.CallAfter(self._update_download_progress, event.data)

    def _update_download_progress(self, progress):
        self.label_downloaded.SetLabel(
            self.label_downloaded.skele % humanise_filesize(progress))

    def wait_on_pid(self, event):
        self.listbook_stage.SetSelection(1)
        
        waiting_done, evt_waiting_done = wx.lib.newevent.NewEvent()
        self.Bind(evt_waiting_done, self.extract)

        waiter = Waiter(self, self.pid, waiting_done)

        waiter.start()

    def extract(self, event):
        self.listbook_stage.SetSelection(2)

        extracting_done_id = wx.NewId()
        extracting_done, evt_extracting_done = wx.lib.newevent.NewEvent()
        self.Bind(evt_extracting_done, self.finished)

        extractor = Extractor(self, extracting_done)

        extractor.start()

    def finished(self, event):
        self.listbook_stage.SetSelection(3)

        os.startfile()

        wx.Exit()

class App(wx.App):
    def __init__(self):
        super(App, self).__init__()

        self._mainframe = Main()

        self.MainLoop()

App()
