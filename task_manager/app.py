import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from process_tree import ProcessTree
from applications_tree import ApplicationTree
from buttons import ProcessKillButton, ProcessTreeUpdateButton
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
        self.aplications_treeview = ApplicationTree()
        applications_scroll = Gtk.ScrolledWindow()
        applications_scroll.set_size_request(400,500)
        applications_scroll.add(self.aplications_treeview)
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
        button_update_tree = ProcessTreeUpdateButton()
        button_update_tree.connect("clicked", self.update_tree)
        button_box.pack_start(button_update_tree, True, True, 0)
        button_kill = ProcessKillButton()
        button_kill.connect("clicked", self.kill_process)
        button_box.pack_start(button_kill, True, True, 0)
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

    def update_tree(self, button):
        self.process_treeview.clean_store()
#        print('clean - OK')
        self.process_treeview.fill_store()
#        print('create - OK')


    def selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter:
            #print(type(treeiter))
            if type(model[treeiter][0]) == str:
                self.selected_key = model[treeiter][0]
            elif type(model[treeiter][0]) == int:
                self.selected_pid = model[treeiter][0]
            dict_info = psutil.Process(self.selected_pid).as_dict()
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
        psutil.Process(self.selected_pid).kill()


if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()