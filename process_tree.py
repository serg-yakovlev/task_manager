import gi
import psutil
import json
from multiprocessing import Process
from threading import Lock
# from datetime import datetime
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ProcessTree(Gtk.TreeView):

    def __init__(self):
        LOCK = Lock()
        self.frozen = False
        self.need_to_change_labels = False
        self.selected_pid = 1
        self.proc_list()
        self.store = Gtk.ListStore(int, str, str, str, float)
        self.fill_store()
        super().__init__(model=self.store.filter_new())
        self.set_size_request(600, 200)
        column_names = ["pid", "name", "username", "application", "memory %"]
        for i, col_n in enumerate(column_names):
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            self.append_column(column)
            if col_n == "memory %":
                column.set_max_width(50)
        self.set_cursor(0, self.get_column(0))
        self.proc_cursor = self.get_cursor()

        def update_proc_list():
            while True:
                with LOCK:
                    self.proc_list()

        p = Process(target=update_proc_list)
        p.start()

        self.proc_update_pid = p.pid

    def fill_store(self, app='(ALL)'):
        if self.frozen:
            return True
        self.updating = True
        try:
            with open('proc_list_json', 'r') as file:
                pr = json.loads(file.read())
        except Exception:
            pass
        else:
            processes = pr if app == '/(ALL)' else [
                p for p in pr if p['file'] == app]
            if processes == []:
                self.updating = False
                return True
            if self.need_to_change_labels:
                self.selected_pid = processes[0]['id']
            self.need_to_change_labels = False
            self.store.clear()
            i = 0
            row = 0
            for proc in processes:
                self.store.append([
                    proc['id'],
                    proc['name'],
                    proc['username'],
                    proc['file'],
                    proc['memory']
                ])
                if proc['id'] == self.selected_pid:
                    row = i
                i += 1
            self.set_cursor(row, self.get_column(0))
            self.proc_counter = i
            self.updating = False
        return True

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
        with open('proc_list_json', 'w') as file:
            json.dump(processes, file)


if __name__ == '__main__':
    w = Gtk.Window(title='Process List')
    t = ProcessTree()
    w.set_size_request(1000, 500)
    master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    w.add(master_box)
    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_size_request(1000, 470)
    master_box.add(scrollable_treelist)
    scrollable_treelist.add(t)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
