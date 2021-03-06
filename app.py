import gi
import psutil
from datetime import datetime
from process_tree import ProcessTree
from applications_tree import ApplicationTree
from buttons import ProcessKillButton
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
        app_adj = Gtk.Adjustment()
        applications_scroll = Gtk.ScrolledWindow(app_adj)
        applications_scroll.set_size_request(400, 500)
        applications_scroll.add_with_viewport(self.applications_treeview)
        left_box.pack_start(applications_tree_box, False, True, 0)
        applications_tree_box.pack_start(applications_scroll, True, True, 0)
        proc_adj = Gtk.Adjustment()
        process_tree_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.pack_start(process_tree_box, False, True, 0)
        self.process_scroll = Gtk.ScrolledWindow(proc_adj)
        self.process_scroll.set_size_request(600, 220)
        process_tree_box.pack_start(self.process_scroll, True, True, 0)
        self.process_treeview = ProcessTree()
        self.process_scroll.add_with_viewport(self.process_treeview)
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box.pack_end(button_box, False, True, 0)
        close_button = Gtk.Button(label="Close")
        close_button.connect("clicked", self.close_app)
        button_box.pack_start(close_button, True, True, 0)
        # self.freeze_button = FreezeButton()
        # self.freeze_button.connect('clicked', self.freeze)
        # button_box.pack_start(self.freeze_button, True, True, 0)
        self.proc_kill_button = ProcessKillButton()
        self.proc_kill_button.connect("clicked", self.kill_process)
        button_box.pack_start(self.proc_kill_button, True, True, 0)
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
        self.closing = False

        def proc_tree_update():
            if self.closing:
                return False
            self.process_treeview.fill_store(
                self.applications_treeview.selected_app
            )
            proc_adj.set_value(0)
            return True

        def app_tree_update():
            if self.closing:
                return False
            self.applications_treeview.fill_store()
            app_adj.set_value(0)
            return True

        GLib.timeout_add_seconds(1, proc_tree_update)
        GLib.timeout_add_seconds(1, app_tree_update)

#    def freeze(self, button):
#        self.process_treeview.frozen = (
#            True if not self.process_treeview.frozen else False
#        )
#        self.applications_treeview.frozen = (
#            True if not self.applications_treeview.frozen else False
#        )
#        button.set_label(
#            label=(
#                'Continue' if self.process_treeview.frozen else 'Freeze')
#        )

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
        self.labels_update()
        self.process_treeview.set_cursor(
            0, self.process_treeview.get_column(0)
        )
        self.process_treeview.app_cursor = (
            self.process_treeview.get_cursor()
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
            self.labels_update()

    def labels_update(self):

        def float_to_date(float_arg):
            date = datetime.fromtimestamp(
                float_arg
            ).strftime('%H:%M:%S %Y-%m-%d')
            return date

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
            if self.keys_tree.selected_key == 'create_time':
                formatted_time = ' ({0})'.format(
                    float_to_date(dict_info['create_time'])
                )
            else:
                formatted_time = ''
            info = '{0}: {1} {2} {3}\n\n'.format(
                self.keys_tree.selected_key,
                dict_info[self.keys_tree.selected_key],
                parent_process, formatted_time
            )
        self.process_info_label.set_text(info[:])

    def kill_process(self, button):
        pid = self.process_treeview.selected_pid
        name = psutil.Process(pid).name()
        try:
            psutil.Process(pid).kill()
        except Exception as e:
            print("Process {0} (PID {1}) can't be killed".format(name, pid))
            print(e)
        else:
            self.process_info_label.set_text(
                'Process {0} {1} killed.'.format(pid, name)
            )
            if self.process_treeview.proc_counter == 1:
                self.applications_treeview.set_cursor(
                    0, self.applications_treeview.get_column(0)
                )
                self.applications_treeview.app_cursor = (
                    self.applications_treeview.get_cursor()
                )
            else:
                self.process_treeview.set_cursor(
                    0, self.process_treeview.get_column(0)
                )
                self.process_treeview.proc_cursor = (
                    self.process_treeview.get_cursor()
                )

    def close_app(self, button):
        psutil.Process(
            self.applications_treeview.app_update_pid
        ).kill()
        psutil.Process(
            self.process_treeview.proc_update_pid
        ).kill()
        self.closing = True
        Gtk.main_quit()


if __name__ == '__main__':
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
