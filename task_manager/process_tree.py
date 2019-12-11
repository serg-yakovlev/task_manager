import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from threading import Thread


class ProcessTree(Gtk.TreeView):

    def __init__(self):
        self.proc_list()

        def proc_list_thread():
            while True:
                self.proc_list()

        th =Thread(target = proc_list_thread)
        th.start()
        try:
            store = self.store
        except Exception:
            self.store = Gtk.ListStore(int, str, str, str, float)
            self.store = self.fill_store()
        super().__init__(model = self.store.filter_new())
        self.set_size_request(600,200)
        column_names = ["pid", "name", "username", "application", "memory %"]
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            self.append_column(column)
            if col_n == "memory %":
                column.set_max_width(50)

    def fill_store(self):
        self.processes = self.curr_proc_list
        for proc in self.processes:
            self.store.append([
                proc['id'],
                proc['name'],
                proc['username'],
                proc['file'],
                proc['memory']
                ])
        return self.store

    def clean_store(self):
        if self.store:
            self.store.clear()

    def proc_list(self):
        processes = []
        for proc in psutil.process_iter():
            try:
                e = proc.exe()
            except psutil.AccessDenied:
                e = None
            proc_dict = proc.as_dict()
            p = {
                'id': proc.pid,
                'name': proc_dict['name'],
                'username': proc_dict['username'],
                'file': e,
                'memory': proc_dict['memory_percent']
                }
            processes.append(p)
        processes.sort(key=lambda x: x['memory'], reverse=True)
        self.curr_proc_list = processes


if __name__ == '__main__':
    w = Gtk.Window(title='Process List')
    t = ProcessTree()
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