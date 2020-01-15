import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf


class ProcessKillButton(Gtk.Button):
    def __init__(self):
        super().__init__(label = 'Kill process')


class ProcessTreeUpdateButton(Gtk.Button):
    def __init__(self):
        super().__init__(label = 'Update process tree')

class FreezeButton(Gtk.Button):
    def __init__(self):
        super().__init__(label = 'Freeze')