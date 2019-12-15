import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib
from process_tree import ProcessTree
from applications_tree import ApplicationTree
from buttons import ProcessKillButton, FreezeButton 
from info_keys_tree import InfoTree

class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Task manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 500)
        self.selected_key = '(ALL)'
        self.selected_pid = 1
        master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(master_box)
        hpaned = Gtk.Paned()
        #hpaned.set_position(300)
        master_box.add(hpaned)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_header = Gtk.Label(label='APPLICATIONS')
        right_header = Gtk.Label(label='PROCESSES')
        left_box.pack_start(left_header, False, True, 0)
        right_box.pack_start(right_header, False, True, 0)
        hpaned.add1(left_box)
        hpaned.add2(right_box)
        applications_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.applications_treeview = ApplicationTree()
        applications_scroll = Gtk.ScrolledWindow()
        applications_scroll.set_size_request(400,500)
        applications_scroll.add(self.applications_treeview)
        left_box.pack_start(applications_tree_box, False, True, 0)
        applications_tree_box.pack_start(applications_scroll, True, True, 0)
        process_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.pack_start(process_tree_box, False, True, 0)
        self.process_scroll = Gtk.ScrolledWindow()
        self.process_scroll.set_size_request(600,220)
        process_tree_box.pack_start(self.process_scroll, True, True, 0)
        self.process_treeview = ProcessTree()
        self.process_scroll.add(self.process_treeview)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box.pack_end(button_box, False, True, 0)
        button_close = Gtk.Button(label="Close")
        button_close.connect("clicked", Gtk.main_quit)
        button_box.pack_start(button_close, True, True, 0)
        #self.button_update_proc_tree = ProcessTreeUpdateButton()
        #self.button_update_proc_tree.connect("clicked", self.update_proc_tree)
        self.freeze_button = FreezeButton()
        self.freeze_button.connect('clicked', self.freeze)
        button_box.pack_start(self.freeze_button, True, True, 0)
        self.button_kill = ProcessKillButton()
        self.button_kill.connect("clicked", self.kill_process)
        button_box.pack_start(self.button_kill, True, True, 0)
        self.process_info_label = Gtk.Label()
        self.process_info_label.set_size_request(430,210)
        self.process_info_label.set_selectable(True)
        self.process_info_label.set_line_wrap(True)
        info_header = Gtk.Label(label='DETAILED PROCESS INFO')
        right_box.pack_start(info_header, True, True, 0)
        keys_scrolled = Gtk.ScrolledWindow()
        self.keys_tree = InfoTree(1)
        keys_scrolled.add(self.keys_tree)
        info_scrolled = Gtk.ScrolledWindow()
        info_scrolled.set_size_request(430,210)
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        info_box.set_size_request(430,210)
        info_box.pack_start(keys_scrolled, True, True, 0)
        info_box.pack_start(info_scrolled, True, True, 0)
        info_scrolled.add(self.process_info_label)
        right_box.add(info_box)
        self.process_select = self.process_treeview.get_selection()
        self.process_select.connect("changed", self.selection_changed)
        self.param_select = self.keys_tree.get_selection()
        self.param_select.connect("changed", self.selection_changed)
        self.app_select = self.applications_treeview.get_selection()
        self.app_select.connect("changed", self.app_selection_changed)

        def proc_tree_update():
            self.process_treeview.fill_store(self.selected_app)
            return True

        GLib.timeout_add_seconds(1, proc_tree_update)
        GLib.timeout_add_seconds(1, self.applications_treeview.fill_store)


    def app_selection_changed(self, selection):
        if self.applications_treeview.updating == True:
            return
        model, treeiter = selection.get_selected()
        if treeiter:
            self.selected_app = model[treeiter][0]+'/'+model[treeiter][1]
            print(self.selected_app)

    def freeze(self, button):
        self.process_treeview.frozen = True if self.process_treeview.frozen == False else False
        button.set_label(label='Continue' if self.process_treeview.frozen == True else 'Freeze')

    def selection_changed(self, selection):
        if self.process_treeview.updating == True:
            return
        model, treeiter = selection.get_selected()
        if treeiter:
            #for item in model:
                #print(item)
            #print(type(treeiter))
            if type(model[treeiter][0]) == str:
                self.selected_key = model[treeiter][0]
            elif type(model[treeiter][0]) == int:
                self.selected_pid = model[treeiter][0]
                print("PID", self.selected_pid, "selected")
            #print(self.selected_pid)
            #print(psutil.Process(self.selected_pid))
            dict_info = psutil.Process(self.selected_pid).as_dict()
            #print(dict_info['name'])
            #print(type(dict_info))
            #print(str(self.selected_key))
            if self.selected_key == '(ALL)':
                info = ''
                for key in dict_info.keys():
                    info = '{0} {1}: {2}\n\n'.format(
                        info, 
                        key, 
                        dict_info[key]
                        )
            else:
                if self.selected_key == 'ppid':
                    parent_process = ' (parent process: {0})'.format(
                        psutil.Process(
                            dict_info['ppid']
                            ).name()
                        ) if self.selected_pid > 1 else '(None)'
                else:
                    parent_process = ''
                info = '{0}: {1} {2}\n\n'.format(
                        self.selected_key, 
                        dict_info[self.selected_key],
                        parent_process,
                        )
            self.process_info_label.set_text(info[:])

    def kill_process(self, button):
        pid = self.selected_pid
        name = psutil.Process(pid).name()
        try:
            psutil.Process(pid).kill()
        except Exception as e:
            print(e)
        else:
            button.set_label(label='Process is killing')
            self.process_treeview.frozen = False
            self.process_treeview.fill_store()
            button.set_label(label='Kill process')
            self.process_info_label.set_text(
                'Process {0} {1} killed.'.format(pid, name)
                )
        self.selected_pid = 1
        self.freeze_button.set_label('Freeze')
        print(self.selected_pid)



if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()