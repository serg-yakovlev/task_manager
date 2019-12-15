import gi
import psutil
import copy
import json
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from multiprocessing import Process
from threading import Thread, Lock
import time

#from subprocess import Popen, PIPE


class ProcessTree(Gtk.TreeView):

    def __init__(self):
        LOCK = Lock()
        self.frozen = False
        self.proc_list()
        self.store = Gtk.ListStore(int, str, str, str, float)
        self.fill_store()
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

        def update_proc_list():
            #nr = 1
            while True:
                #time.sleep(1)
                with LOCK:
                    self.proc_list()
                #print(nr)
                #nr += 1

        p = Process(target=update_proc_list)
        p.start()

        #def update_store():
        #    while True:
        #        time.sleep(1)
        #        with LOCK:
        #            self.fill_store()

        #th = Thread(target=update_store)
        #th.start()

    def fill_store(self):
        if self.frozen == True:
            return True
        self.updating = True
        try:
            with open('proc_list_json', 'r') as file:
                processes = json.loads(file.read())
            #print('json load')
        except Exception as e:
            print('Exception while load proc_json:', e)
        else:
            if self.store:
                self.store.clear()
            if processes == []:
                return True
            #time.sleep(1)
            #i = 0
            for proc in processes:
                #time.sleep(0)
                #print('append start - proc', i)
                #print(
                #    proc['id'],
                #    proc['name'],
                #    proc['username'],
                #    proc['file'],
                #    proc['memory']
                #    )
                self.store.append([
                    proc['id'],
                    proc['name'],
                    proc['username'],
                    proc['file'],
                    proc['memory']
                    ])
                #print('append finished - proc', i)
                #i += 1
        #print('fill_store_finish\n\n')
        self.updating = False
        return True

    def clean_store(self):
        if self.store:
            self.store.clear()

    def proc_list(self):
        #print('iter_process')
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
        #self.curr_proc_list = copy.deepcopy(processes)


if __name__ == '__main__':
    w = Gtk.Window(title='Process List')
    t = ProcessTree()
    w.set_size_request(1000, 500)
    master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    w.add(master_box)
    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_size_request(1000,470)
    master_box.add(scrollable_treelist)
    scrollable_treelist.add(t)
    w.connect("destroy", Gtk.main_quit)
    w.show_all()
    Gtk.main()