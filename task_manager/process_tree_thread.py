import gi
import psutil
import copy
import json
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib
from multiprocessing import Process
from threading import Thread, Lock
import time

#from subprocess import Popen, PIPE


class ProcessTree(Gtk.TreeView):

    def __init__(self):
        #self.proc_list()
        self.store = Gtk.ListStore(int, str, str, str, float)
        self.fill_store()
        super().__init__(model=self.store)
        self.set_size_request(600,200)
        column_names = ["pid", "name", "username", "application", "memory %"]
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            self.append_column(column)
            if col_n == "memory %":
                column.set_max_width(50)

    def print_in_log(self, text):
        with open('log', 'a') as file:
            file.write(text)

    def store_update(self):
        i = 0
        #while True:
        self.print_in_log('                            iter'+str(i)+'\n\n')
        i += 1
        time.sleep(5)
        self.print_in_log('fill_store_start\n\n')
        if self.store:
            self.store.clear()
            self.print_in_log('store clear\n\n')
        processes = self.proc_list()
        i = 0
        for proc in processes:
            time.sleep(0)
            self.print_in_log('append start - proc'+str(i)+'\n\n')
            #self.print_in_log(
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
            self.print_in_log('append finished - proc'+str(i)+'\n\n')
            i += 1
        self.print_in_log('fill_store_finish\n\n')

    def fill_store(self):
        self.print_in_log('fill_store_start\n\n')
        if self.store:
            self.store.clear()
            self.print_in_log('store clear\n\n')
        processes = self.proc_list()
        i = 0
        for proc in processes:
            time.sleep(0)
            self.print_in_log('store append start - proc'+str(i)+'\n\n')
            #self.print_in_log(
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
            self.print_in_log('store append finished - proc'+str(i)+'\n\n')
            i += 1
        self.print_in_log('fill_store_finish \n\n')
        return True

    def clean_store(self):
        if self.store:
            self.store.clear()

    def proc_list(self):
        self.print_in_log('proc_list start\n\n')
        processes = []
        i = 0
        for proc in psutil.process_iter():
            self.print_in_log('          psutil_iter'+str(i)+'\n\n')
            i += 1
            self.print_in_log('          increment'+str(i)+'\n\n')
            try:
                exe_file = proc.exe()
            except psutil.AccessDenied:
                exe_file = None
            self.print_in_log('          exe file'+str(exe_file)+'\n\n')
            proc_dict = proc.as_dict()
            self.print_in_log('          dict_created\n\n')
            p = {
                'id': proc.pid,
                'name': proc_dict['name'],
                'username': proc_dict['username'],
                'file': exe_file,
                'memory': proc_dict['memory_percent']
                }
            self.print_in_log('          json_item_created\n\n')
            processes.append(p)
            self.print_in_log('          proc append\n\n')
        self.print_in_log('proc_list finish')
        processes.sort(key=lambda x: x['memory'], reverse=True)
        return processes
        #self.curr_proc_list = copy.deepcopy(processes)


if __name__ == '__main__':
    w = Gtk.Window(title='Process List')
    t = ProcessTree()
    w.set_size_request(1000, 500)
    master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    w.add(master_box)
    button = Gtk.Button()

    def update(button):
        t.fill_store()

    button.connect("clicked", update)
    scrollable_treelist = Gtk.ScrolledWindow()
    scrollable_treelist.set_size_request(1000,470)
    master_box.pack_start(scrollable_treelist, False, False, 0)
    master_box.pack_start(button, False, False, 0)
    scrollable_treelist.add(t)

    def upd_thread():
        # for i in range(5):
        i = 0
        while True:
            #time.sleep(5)
            t.print_in_log('                                iter'+str(i)+'\n\n')
            i += 1
            t.fill_store()

    w.connect("destroy", Gtk.main_quit)
    w.show_all()

    p = Process(target=upd_thread)
    p.start()
    #upd_thread()

    Gtk.main()