import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
import os, time


class MainWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="File manager")
        self.connection = None
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(1000, 600)
        master_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(master_box)

        button_box = Gtk.Box()
        master_box.pack_start(button_box, False, False, 0)

        hpaned = Gtk.Paned()
        hpaned.set_position(600)
        master_box.add(hpaned)
        
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_size_request(250, -1)
        hpaned.add1(left_box)
        label = Gtk.Label(label='Left side is here...')
        left_box.pack_start(label, False, True, 20)
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        print("right box:   ", right_box)
        right_box.set_size_request(250, -1)
        hpaned.add2(right_box)
        label = Gtk.Label(label="...and Right side is here (don't confuse)")
        right_box.pack_start(label, False, True, 20)

        def butt_click(args):
            box, text = args
            print(box, text)
            label = Gtk.Label(label=text)
            label = Gtk.Label(label="111")
            right_box.pack_start(label, False, True, 0)
            print(master_box)
            master_box.pack_start(label, False, True, 0)

        buttons=[]
        for i in range(5):
        	buttons.append(Gtk.Button(label = "Button {0}".format(i)))
        	a = Callback(butt_click, (right_box, "Button {0}".format(i)))
        	buttons[i].connect("clicked", a)
        	button_box.pack_start(buttons[i], False, False, 0)

        file_list = os.listdir(".")
        #label = Gtk.Label(label=file_list)
        #label.set_line_wrap(True)
        #left_box.pack_start(label, False, True, 0)

        dir_list = []
        not_dir = []
        for item in file_list:
            if os.path.isdir(item):
                dir_list.append([item, "folder"])
            else:
                not_dir.append([item, "file"])
        dir_list.sort()
        not_dir.sort()
        new_file_list = dir_list + not_dir


        updated_list = []
        for item in new_file_list:
            size = os.path.getsize(item[0])
            datec = time.ctime(os.path.getctime(item[0]))
            datem = time.ctime(os.path.getmtime(item[0]))
            updated_list.append([item[0], item[1], size, datec, datem])

        file_store = Gtk.ListStore(str, str, int, str, str)
        for file_row in updated_list:
            file_store.append(file_row)
        model = file_store.filter_new()
        treeview = Gtk.TreeView.new_with_model(model)
#        renderer = Gtk.CellRendererText()
#        column = Gtk.TreeViewColumn("file", Gtk.CellRendererText(), text=0)

        column_names = ["file name", "type", "size", "created", "last changed"]
        for i, col_n in enumerate(column_names):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(col_n, Gtk.CellRendererText(), text=i)
            treeview.append_column(column)


#        scrollable_treelist = Gtk.ScrolledWindow()
#        left_box.pack_start(scrollable_treelist, True, True, 5)
#        scrollable_treelist.add(treeview)

        left_box.pack_start(treeview, False, True, 0)




class Callback:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def __call__(self, args):
        self.func(*self.args, **self.kwargs)







if __name__ == '__main__':

    #print(dir(Gtk.Entry.connect.__name__))
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
