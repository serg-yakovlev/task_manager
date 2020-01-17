import gi
import psutil
from process_tree import ProcessTree
from applications_tree import ApplicationTree
from buttons import ProcessKillButton, FreezeButton
from info_keys_tree import InfoTree
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="Task manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 500)
        master_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(master_box)
        hpaned = Gtk.Paned()
        master_box.add(hpaned)
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        app_header = Gtk.Label(label='APPLICATIONS')
        self.proc_header = Gtk.Label(label='PROCESSES')
        left_box.pack_start(app_header, False, True, 0)
        right_box.pack_start(self.proc_header, False, True, 0)
        hpaned.add1(left_box)
        hpaned.add2(right_box)
        applications_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.applications_treeview = ApplicationTree()
        applications_scroll = Gtk.ScrolledWindow()
        applications_scroll.set_size_request(400, 500)
        applications_scroll.add(self.applications_treeview)
        left_box.pack_start(applications_tree_box, False, True, 0)
        applications_tree_box.pack_start(applications_scroll, True, True, 0)
        process_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.pack_start(process_tree_box, False, True, 0)
        self.process_scroll = Gtk.ScrolledWindow()
        self.process_scroll.set_size_request(600, 220)
        process_tree_box.pack_start(self.process_scroll, True, True, 0)
        self.process_treeview = ProcessTree()
        self.process_scroll.add(self.process_treeview)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box.pack_end(button_box, False, True, 0)
        button_close = Gtk.Button(label="Close")
        button_close.connect("clicked", Gtk.main_quit)
        button_box.pack_start(button_close, True, True, 0)
        self.freeze_button = FreezeButton()
        self.freeze_button.connect('clicked', self.freeze)
        button_box.pack_start(self.freeze_button, True, True, 0)
        self.button_kill = ProcessKillButton()
        self.button_kill.connect("clicked", self.kill_process)
        button_box.pack_start(self.button_kill, True, True, 0)
        self.process_info_label = Gtk.Label()
        self.process_info_label.set_size_request(430, 210)
        self.process_info_label.set_selectable(True)
        self.process_info_label.set_line_wrap(True)
        self.info_header = Gtk.Label(label='DETAILED PROCESS INFO')
        right_box.pack_start(self.info_header, True, True, 0)
        keys_scrolled = Gtk.ScrolledWindow()
        self.keys_tree = InfoTree(1)
        keys_scrolled.add(self.keys_tree)
        info_scrolled = Gtk.ScrolledWindow()
        info_scrolled.set_size_request(430, 210)
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        info_box.set_size_request(430, 210)
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
        self.applications_treeview.selected_app = '/(ALL)'

        def proc_tree_update():
            self.process_treeview.fill_store(
                self.applications_treeview.selected_app
            )
            return True

        def app_tree_update():
            self.applications_treeview.fill_store()
            return True

        GLib.timeout_add_seconds(1, proc_tree_update)
        GLib.timeout_add_seconds(1, app_tree_update)

    def freeze(self, button):
        self.process_treeview.frozen = (
            True if not self.process_treeview.frozen else False
        )
        self.applications_treeview.frozen = (
            True if not self.applications_treeview.frozen else False
        )
        button.set_label(
            label=(
                'Continue' if self.process_treeview.frozen else 'Freeze')
        )

    def app_selection_changed(self, selection):
        if self.applications_treeview.updating:
            return
        model, treeiter = selection.get_selected()
        self.applications_treeview.selected_app = model[treeiter][0] + \
            '/' + model[treeiter][1]
        self.proc_header.set_text('PROCESSES ({0})'.format(
            self.applications_treeview.selected_app))
        self.process_treeview.need_to_change_labels = True
        self.process_treeview.fill_store(
            self.applications_treeview.selected_app)
        name = psutil.Process(
            self.process_treeview.selected_pid
        ).as_dict(attrs=['name'])['name']
        self.info_header.set_text(
            'DETAILED PROCESS INFO ({0} {1})'.format(
                self.process_treeview.selected_pid,
                name)
        )
        self.process_info_label.set_text(
            'name: {0}\n\n'.format(
                name)
        )

    def selection_changed(self, selection):
        if self.process_treeview.updating:
            return
        model, treeiter = selection.get_selected()
        if treeiter:
            if type(model[treeiter][0]) == str:
                self.keys_tree.selected_key = model[treeiter][0]
            elif type(model[treeiter][0]) == int:
                self.process_treeview.selected_pid = model[treeiter][0]
                self.info_header.set_text(
                    'DETAILED PROCESS INFO ({0} {1})'.format(
                        self.process_treeview.selected_pid,
                        model[treeiter][1]
                    )
                )
            dict_info = psutil.Process(
                self.process_treeview.selected_pid).as_dict()
            if self.keys_tree.selected_key == '(ALL)':
                info = ''
                for key in dict_info.keys():
                    info = '{0} {1}: {2}\n\n'.format(
                        info,
                        key,
                        dict_info[key]
                    )
            else:
                if self.keys_tree.selected_key == 'ppid':
                    parent_process = ' (parent process: {0})'.format(
                        psutil.Process(
                            dict_info['ppid']
                        ).name()
                    ) if self.process_treeview.selected_pid > 1 else '(None)'
                else:
                    parent_process = ''
                info = '{0}: {1} {2}\n\n'.format(
                    self.keys_tree.selected_key,
                    dict_info[self.keys_tree.selected_key],
                    parent_process,
                )
            self.process_info_label.set_text(info[:])

    def kill_process(self, button):
        pid = self.process_treeview.selected_pid
        name = psutil.Process(pid).name()
        try:
            self.process_treeview.selected_pid = 1
            psutil.Process(pid).kill()
        except Exception as e:
            pass
        else:
            self.process_info_label.set_text(
                'Process {0} {1} killed.'.format(pid, name)
            )


if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
