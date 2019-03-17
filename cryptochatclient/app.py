import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import os

class CryptoChat(Gtk.Window):
    def __init__(self):
        self.builder = Gtk.Builder()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        glade_file = os.path.join(root_dir, 'resources/ui/visual.glade')
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)

        self.login = self.builder.get_object('loginDialog')
        self.login.show_all()

        response = self.login.run()
        if response == Gtk.ResponseType.OK:
            self.loginInput = self.builder.get_object("loginID")
            print('logiin', self.loginInput)
            inputMessageText = self.loginInput.get_text()
            print('inpout', inputMessageText)
            if inputMessageText == '1234':
                print('fasfd', inputMessageText)
                print('Login successful')
                self.logged()
            else:
                print('Error')
                print('fasfd', inputMessageText)
                self.loginInput.set_text('')
            pass
            # self.login.hide()
        elif response == Gtk.ResponseType.CANCEL:
            self.login.hide()

        Gtk.main()
        
    def onDestroy(self):
        Gtk.main_quit()

    def logged(self):
        self.window = self.builder.get_object('window1')
        self.window.show_all()
    
    def onTextViewSet(self, textView, inputMessage):
        self.textview = self.builder.get_object("chatWindow")
        text_buffer = self.textview.get_buffer()
        end_iter = text_buffer.get_end_iter()
        if inputMessage:
            text_buffer.insert(end_iter, '\n\nMe:\n' + inputMessage)

    def onSendMessageButtonPressed(self, button):
        # TODO: send message to DB (server)
        inputMessage = self.builder.get_object("message")
        inputMessageText = inputMessage.get_text()
        self.onTextViewSet(self, inputMessageText)
        self.builder.get_object("message").set_text('')

    # Add contact/new conversation to listbox
    def addContact(self, inputName, listName):
        name = self.builder.get_object(inputName).get_text()
        self.builder.get_object(inputName).set_text('')
        label = Gtk.Label()
        label.set_text(name)
        newItem = Gtk.ListBoxRow()
        newItem.add(label)
        newItem.show_all()
        listbox = self.builder.get_object(listName)
        listbox.add(newItem)

    # Dialog for adding new conversation to list
    def onNewConversationButtonPressed(self, button):
        dialog = self.builder.get_object('dialogConversation')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.addContact("conversationTextInput", "conversationsList")
            dialog.hide()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()

    # Dialog for adding user do contact list
    def onAddContactButtonPressed(self, button):
        dialog = self.builder.get_object('dialogAddContact')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.addContact("contactIdTextInput", "contactList")
            dialog.hide()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()
    
def run():
    app = CryptoChat()
    app.run()
