import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import os, time, re
from subprocess import Popen, PIPE


class MainWindow(Gtk.Window):

    def __init__(self):

        def on_tree_selection_changed(selection):
            model, treeiter = selection.get_selected()
            if treeiter:
                self.selected_pid = model[treeiter][0]
                dict_info = psutil.Process(self.selected_pid).as_dict()
                info = 'DETAILED PROCESS INFO: \n\n'
                for key in dict_info.keys():
                    info = '{0} {1}: {2}\n\n'.format(
                        info, 
                        key, 
                        dict_info[key]
                        )
                    info_label.set_text(info[:])

        def kill_process(button):
            psutil.Process(self.selected_pid).kill()

        super().__init__(title="Task manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 500)
        master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(master_box)
        hpaned = Gtk.Paned()
        #hpaned.set_position(600)
        master_box.add(hpaned)
        tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.pack_start(tree_box, False, True, 0)
        hpaned.add1(left_box)
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_size_request(570,470)
        tree_box.pack_start(self.scrollable_treelist, True, True, 0)
        self.treeview = self.create_tree()
        self.scrollable_treelist.add(self.treeview)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        left_box.pack_end(button_box, False, True, 0)
        button_close = Gtk.Button(label="Close")
        button_close.connect("clicked", Gtk.main_quit)
        button_box.pack_start(button_close, True, True, 0)
        button_update_tree = Gtk.Button(label="Update tree")
        button_update_tree.connect("clicked", self.update_tree)
        button_box.pack_start(button_update_tree, True, True, 0)
        button_kill = Gtk.Button(label="Kill process")
        button_kill.connect("clicked", kill_process)
        button_box.pack_start(button_kill, True, True, 0)
        info_label = Gtk.Label()
        info_label.set_size_request(430,500)
        #info_label.set_markup('Here should be process detailed info')
        info_label.set_selectable(True)
        info_label.set_line_wrap(True)
        info_box = Gtk.ScrolledWindow()
        info_box.set_size_request(430,500)
        info_frame = Gtk.Frame()
        info_frame.set_size_request(430,500)
        info_frame.add(info_box)
        info_box.add(info_label)
        hpaned.add2(info_frame)
        self.select = self.treeview.get_selection()
        self.select.connect("changed", on_tree_selection_changed)

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
        for item in store:
            pass #print(item)
        model = store.filter_new()
        treeview = Gtk.TreeView.new_with_model(model)
        column_names = ["pid", "name", "username", "application", "memory %"]
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            column.set_resizable(True)
            treeview.append_column(column)
            if col_n == "memory %":
                column.set_max_width(50)
        self.treeview = treeview
        return self.treeview

    def update_tree(self, button):
        self.scrollable_treelist.remove(self.treeview)
        print('OK 1')
        self.create_tree()
        print('OK 2')
        self.scrollable_treelist.add(self.treeview)
        print('OK 3')


if __name__ == '__main__':

    #print(dir(Gtk.Entry.connect.__name__))
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()