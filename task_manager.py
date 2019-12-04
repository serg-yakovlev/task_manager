import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import os, time, re
from subprocess import Popen, PIPE


class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Task manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 600)
        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(master_box)
        tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        master_box.pack_start(tree_box, False, True, 0)
        scrollable_treelist = Gtk.ScrolledWindow()
        scrollable_treelist.set_size_request(500,500)
        tree_box.pack_start(scrollable_treelist, True, True, 0)
        treeview = self.create_tree()
        scrollable_treelist.add(treeview)
        button_close = Gtk.Button(label="Close")
        button_close.connect("clicked", Gtk.main_quit)
        master_box.pack_start(button_close, False, False, 0)

    def create_process_list(self):
        proc = Popen(['ps', '-eo' ,'pid,args'], stdout=PIPE, stderr=PIPE)
        stdout, notused = proc.communicate()
        processes = re.split(r'\n', stdout.decode('utf-8'))
        pids = []
        commands = []
        for process in processes[1:]:
            if process:
                pattern_pid = r'\s*(\d*)\s*\S[\s\S]*'
                pattern_command = r'\s*\d*\s([\s\S]*)'
                pid = re.findall(pattern_pid, process)
                command = re.findall(pattern_command, process)
                pids.append(int(pid[0]))
                commands.append(command[0])
                #print(pid[0], command[0])
        return [pids, commands]

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
                'memory': proc_dict['memory_percent'],
                'mem_info': proc.memory_info()
                }
            processes.append(p)
            #print(
            #    type(p['id']),
            #    type(p['name']),
            #    type(p['username']),
            #    type(p['file']),
            #    type(p['memory']),
            #    type(p['mem_info'])
            #    )
        processes.sort(key=lambda x: x['memory'], reverse=True)
        return processes

    def create_tree(self):
        processes = self.proc_list()
        store = Gtk.ListStore(int, str, str, str, float)
        for proc in processes:
            store.append([
                proc['id'],
                proc['name'],
                proc['username'],
                proc['file'],
                proc['memory']
                ])
        model = store.filter_new()
        treeview = Gtk.TreeView.new_with_model(model)
        column_names = ["pid", "name", "username", "file", "memory %"]
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            treeview.append_column(column)
        return treeview


if __name__ == '__main__':

    #print(dir(Gtk.Entry.connect.__name__))
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()