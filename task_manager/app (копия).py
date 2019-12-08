import gi
import psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from process_tree import ProcessTree
from buttons import ProcessKillButton, ProcessTreeUpdateButton


class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Task manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 500)
        master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(master_box)
        hpaned = Gtk.Paned()
        #hpaned.set_position(600)
        master_box.add(hpaned)
        process_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.pack_start(process_tree_box, False, True, 0)
        hpaned.add1(left_box)
        self.process_scroll = Gtk.ScrolledWindow()
        self.process_scroll.set_size_request(570,470)
        process_tree_box.pack_start(self.process_scroll, True, True, 0)
        self.process_treeview = ProcessTree()
        self.process_scroll.add(self.process_treeview)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        left_box.pack_end(button_box, False, True, 0)
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
        self.process_info_label.set_size_request(430,500)
        self.process_info_label.set_selectable(True)
        self.process_info_label.set_line_wrap(True)
        info_box = Gtk.ScrolledWindow()
        info_box.set_size_request(430,500)
        info_frame = Gtk.Frame()
        info_frame.set_size_request(430,500)
        info_frame.add(info_box)
        info_box.add(self.process_info_label)
        hpaned.add2(info_frame)
        self.process_select = self.process_treeview.get_selection()
        self.process_select.connect("changed", self.process_selection_changed)

    def update_tree(self, button):
        self.process_scroll.remove(self.process_treeview)
        print('OK 1')
        self.process_treeview = ProcessTree()
        print('OK 2')
        self.process_scroll.add(self.process_treeview)
        print('OK 3')

    def process_selection_changed(self, selection):
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
                self.process_info_label.set_text(info[:])

    def kill_process(button):
        psutil.Process(self.selected_pid).kill()


if __name__ == '__main__':

    #print(dir(Gtk.Entry.connect.__name__))
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()