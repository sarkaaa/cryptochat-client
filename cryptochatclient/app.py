import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os

class CryptoChat:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file('./cryptochatclient/resources/ui/visual.glade')
        self.builder.connect_signals(self)
        
        self.window = self.builder.get_object('window1')
        self.window.show_all()
        Gtk.main()
        
    def onDestroy(self):
        Gtk.main_quit()
    
    def onTextViewSet(self, textView, inputMessage):
        self.textview = self.builder.get_object("chatWindow")
        textbuffer = self.textview.get_buffer() 
        end_iter = textbuffer.get_end_iter()
        if inputMessage:
            textbuffer.insert(end_iter, '\n\nMe:\n' + inputMessage)

    def onButtonPressed(self, button):
        # TODO: send message to DB (server)
        inputMessage = self.builder.get_object("message").get_text()
        self.onTextViewSet(self, inputMessage)
        self.builder.get_object("message").set_text('')
    
def run():
    app = CryptoChat()
