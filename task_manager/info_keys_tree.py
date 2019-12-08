import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf


class InfoTree(Gtk.TreeView):

    def __init__(self, pid):
        info_keys = psutil.Process(pid).as_dict().keys()
        keys = [key for key in info_keys]
        keys.sort()
        store = Gtk.ListStore(str)
        store.append(['(ALL)'])
        for key in keys:
            store.append([key])
        super().__init__(model = store.filter_new())
        self.set_size_request(200,200)
        column_names = ['parameter']
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            self.append_column(column)


if __name__ == '__main__':
    w = Gtk.Window(title='process info keys')
    t = InfoTree(3517)
    w.set_size_request(1000, 500)
    master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    w.add(master_box)
    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_size_request(570,470)
    master_box.add(scrollable_treelist)
    scrollable_treelist.add(t)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()