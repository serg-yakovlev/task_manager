import gi
import psutil
from multiprocessing import Process
from threading import Lock
import os
import json
# from datetime import datetime
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ApplicationTree(Gtk.TreeView):

    def __init__(self):
        LOCK = Lock()
        self.updating = False
        self.frozen = False
        applications = self.app_list()
        self.store = Gtk.ListStore(str, str, float)
        for app in applications:
            self.store.append(app)
        super().__init__(model=self.store)
        self.set_size_request(400, 200)
        column_names = ["path", ".exe", "memory %"]
        for i, col_n in enumerate(column_names):
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            self.append_column(column)
            if col_n == "memory %":
                column.set_max_width(50)
        self.set_cursor(0, self.get_column(0))
        self.app_cursor = self.get_cursor()

        def update_app_list():
            while True:
                with LOCK:
                    self.app_list()

        p = Process(target=update_app_list)
        p.start()
        self.app_update_pid = p.pid

    def fill_store(self):
        self.updating = True
        try:
            with open('app_list_json', 'r') as file:
                applications = json.loads(file.read())
        except Exception:
            pass
        else:
            self.store.clear()
            i = 0
            row = 0
            for app in applications:
                self.store.append(app)
                if app[0] + '/' + app[1] == self.selected_app:
                    row = i
                i += 1
            self.set_cursor(row, self.get_column(0))
            self.updating = False
        return True

    def app_list(self):
        applications = {}
        full_mem = 0
        for proc in psutil.process_iter():
            mem = proc.as_dict(attrs=['memory_percent'])['memory_percent']
            try:
                exe = proc.exe()
            except Exception:
                pass
            else:
                full_mem += mem
                if exe in applications.keys():
                    applications[exe] += mem
                else:
                    applications.update({exe: mem})
        applications.update({'(ALL)': full_mem})
        app_list = []
        for app in applications.keys():
            app_list.append(
                [os.path.split(app)[0],
                 os.path.split(app)[1],
                 applications[app]]
            )
        app_list.sort(key=lambda x: x[2], reverse=True)
        with open('app_list_json', 'w') as file:
            json.dump(app_list, file)
        return app_list


if __name__ == '__main__':
    w = Gtk.Window(title='application List')
    t = ApplicationTree()
    w.set_size_request(1000, 500)
    master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    w.add(master_box)
    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_size_request(570, 470)
    master_box.add(scrollable_treelist)
    scrollable_treelist.add(t)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()
