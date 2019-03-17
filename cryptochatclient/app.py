import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os

class ConversationDialog(Gtk.Dialog):
    def __init__(self, builder):
        self.conversationWindow = builder.get_object('dialogConversation')
        # self.conversationWindow.run()
        # self.conversationWindow.hide()

class AddContactDialog(Gtk.Dialog):
    def __init__(self, builder):
        self.addContactWindow = builder.get_object('dialogAddContact')
        self.addContactWindow.run()
        self.addContactWindow.hide()

class CryptoChat(Gtk.Window):
    def __init__(self):
        self.builder = Gtk.Builder()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        glade_file = os.path.join(root_dir, 'resources/ui/visual.glade')
        self.builder.add_from_file(glade_file)
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

    def onSendMessageButtonPressed(self, button):
        # TODO: send message to DB (server)
        inputMessage = self.builder.get_object("message")
        inputMessageText = inputMessage.get_text()
        self.onTextViewSet(self, inputMessageText)
        self.builder.get_object("message").set_text('')

    def onNewConversationButtonPressed(self, button):
        dialog = self.builder.get_object('dialogConversation').run()
        # response = dialog.run()

        if dialog == Gtk.ResponseType.OK:
            text = self.builder.get_object("conversationTextInput").get_text()
            print('nazev konversaze: ', text)
            dialog.hide()
        elif dialog == Gtk.ResponseType.CANCEL:
            dialog.hide()

    def onAddContactButtonPressed(self, button):
        AddContactDialog(self.builder)

    def onStornoButtonPressed(self, button):
        print('blabla')
    
def run():
    app = CryptoChat()
    app.run()
