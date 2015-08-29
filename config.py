# -*- encoding: cp1252 -*-
lowest_stash_tab_number = 1
highest_stash_tab_number = 65
extra_stash_tabs = [
    u"r",
    u"\u0277",
    ]

###############################################################################
stash_tabs = [str(x) for x in xrange(lowest_stash_tab_number,
                                     highest_stash_tab_number + 1)]
stash_tabs.extend(extra_stash_tabs)
sleepytime = 1