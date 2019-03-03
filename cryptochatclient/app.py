import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

def run():
    window = CryptoChat()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

class CryptoChat(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="CryptoChat")
        self.set_size_request(800, 650)
        hbox = Gtk.Box(spacing=10)
        hbox.set_homogeneous(False)
        vbox_left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_left.set_homogeneous(False)
        vbox_right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_right.set_homogeneous(False)
        
        #self.horizontalPane = Gtk.HPaned()
        self.verticalPane = Gtk.VPaned()
        paneBox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        paneBox1.set_homogeneous(False)

        self.textBox = Gtk.Entry()
        self.btnSend = Gtk.Button(label="Send message")
        self.btnSend.connect("clicked", self.btn_send)

        self.sidebar = Gtk.Frame(label="Contacts")
        self.sidebar.set_label_align(0.05, 0.5)

        self.chatArea = Gtk.Frame(label="Chat area")
        self.chatArea.set_label_align(0.05, 0.5)
        
        #self.mainBox.pack_start(self.horizontalPane, True, True, 0)
        #self.horizontalPane.pack1(self.sidebar, True, True)
        #self.horizontalPane.pack2(self.verticalPane, True, True)
        paneBox1.pack_start(self.textBox, True, True, 0)
        paneBox1.pack_start(self.btnSend, True, True, 0)

        self.verticalPane.pack1(self.chatArea, True, True)
        self.verticalPane.pack2(paneBox1, True, True)

        hbox.pack_start(vbox_left, True, True, 0)
        hbox.pack_start(vbox_right, True, True, 0)
        
        vbox_left.pack_start(self.sidebar, True, True, 0)
        vbox_right.pack_start(self.verticalPane, True, True, 0)

        self.add(hbox)

    def btn_clicked(self, widget):
        self.lbl.set_markup("<span foreground='#599128' size='x-large'>Here!</span>")

    def btn_send(self, widget):
        print ('Message was sent.')
