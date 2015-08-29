# What are the Chances?

(About 30 for 28 tabs of loot, and 77 for 65.  Who knew).

## A simple recipe finder for Path of Exile

What are the Chances is a parasite, feeding on Acquisition's data.  If you're logged into Acquisition, and it's keeping your items updated, you can use this program.

In return for the delicious data feed, What are the Chances finds recipes for you, and sorts them into inventory sized chunks, for easy vendoring.

As it stands, What are the Chances only finds Chance/Alchemy orb recipes.  Personally I don't find it hard to do any of the other ones manually, so I didn't bother including them, but it's expandable.

## How to use it

Pick some tabs in which to dump loot ingame.  The more the better.  I have 119 stash tabs, and 66 of them are dedicated to this.

Open `config.py` in your favourite plaintext editor (no Microsoft Word allowed), and edit the values for `lowest_stash_tab_number`, `highest_stash_tab_number`, and `extra_stash_tabs` to match the aforementioned tabs.  In my case, `lowest_stash_tab_number` is `1`, `highest_stash_tab_number` is `65`, and the contents of `extra_stash_tabs` is just one tab, called `u"r"`.  For extra stash tabs, just add a line between the square brackets, and type `u"your stash tab name",`, making sure to include the trailing comma.  For unicode characters, you'll have to find the code and put that in instead like `u"\u0277"`.

Once that's done, save it, and run `main.pyw`.

# Requirements

What are the Chances depends upon only a few things; below I've provided the download links for them for windows.

[Python](https://www.python.org/ftp/python/2.7.10/python-2.7.10.msi)

[Pygame](http://pygame.org/ftp/pygame-1.9.1.win32-py2.7.msi)

[wx](http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe)

[Virustotal](http://www.virustotal.com), because you should never trust random download links to executables.

For Linux users, this _should_ work, just get wxpython 3+, Python 2.7, and pygame1.9.x, but no promises, (and what are you doing trying to game on linux?)

# Issues

I made this mostly for myself, but whatever, if you find any issues that keep you from using it, gimme a shout.  saraandzuka+watc@gmail.com or @Oddish ingame.
