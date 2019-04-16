"""
CryptoChat client main module.
"""
import os
from gi.repository import Gtk
import gi
gi.require_version("Gtk", "3.0")

class CryptoChat(Gtk.Application):
    """
    CryptoChat client GUI class.
    :param error_text:
    :return:
    """
    def __init__(self):
        """
        Init.
        :param error_text:
        :return:
        """
        self.builder = Gtk.Builder()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        glade_file = os.path.join(root_dir, 'resources/ui/visual.glade')
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)

        self.login_window = self.builder.get_object('login_dialog')
        self.login_window.show_all()

        self.contacts = []

        # .signals.row_selected
        # response = self.login_window.run()
        Gtk.main()

    def on_destroy(self):
        """
        On destroy function.
        :param error_text:
        :return:
        """
        Gtk.main_quit()

    def login(self, arg):
        """
        Login function.
        :param error_text:
        :returm:
        """
        self.login_window = self.builder.get_object('login_dialog')
        self.login_input = self.builder.get_object("login_id")
        input_message_text = self.login_input.get_text()
        if input_message_text == '1234':
            print('Login successful')
            self.login_window.hide()
            self.logged()
        else:
            print('Error')
            self.login_input.set_text('')

    def logged(self):
        """
        Open main window after succesful login.
        :param error_text:
        :return:
        """
        self.window = self.builder.get_object('main_window')
        self.window.show_all()

    # def load_contacts():
        #funkce pro nacitani kontaktu z databaze
    
    # def load_conversations():
        #funkce pro nacitani konverzaci z databaze

    def on_text_view_set(self, input_message):
        """
        Set the messages in chat window.
        :param error_text:
        :return:
        """
        text_view = self.builder.get_object("chat_window")
        text_buffer = text_view.get_buffer()
        end_iter = text_buffer.get_end_iter()
        if input_message:
            text_buffer.insert(end_iter, '\n\nMe:\n' + input_message)

    def update_messages(self):
        # TODO
        return 0

    def on_send_message_button_pressed(self, arg):
        """
        Send message.
        :param error_text:
        :return:
        """
        input_message = self.builder.get_object("message")
        input_message_text = input_message.get_text()
        # TODO: vlozeni zpravy do databaze
        self.on_text_view_set(input_message_text)
        return (self.builder.get_object("message").set_text(''), arg)

    def contact_enter(self, arg):
        """
        Add new contact to contact list.
        :param error_text:
        :return:
        """
        self.add_contact("contact_id_text_input", "contact_name_text_input")
        dialog = self.builder.get_object('dialog_contact')
        dialog.hide()


    def add_contact(self, input_id, input_name):
        """
        Show dialog for adding new contact/conversation.
        :param error_text:
        :return:
        """
        contact_id = self.builder.get_object(input_id).get_text()
        name = self.builder.get_object(input_name).get_text()
        if name != '' and contact_id != '':
            # TODO: request do DB s pridanim uzivatele dle jeho id
            # vypis pridaneho uzivatele v aplikaci
            self.contacts.append({ "contact_id" : contact_id, "alias" : name, "selected": False })
            label = Gtk.Label()
            label.set_text(name)
            contact_item = self.builder.get_object("contact_list_box")
            contact_item.add(label)
            contact_item.show_all()
            print('self,', self.contacts)
        self.builder.get_object(input_name).set_text('')
        self.builder.get_object(input_id).set_text('')

    def on_row_activated(self, list, arg):
        """
        Show dialog for adding new contact/conversation.
        :param error_text:
        :return:
        """
        print("ahhoooj")
        return arg

    def add_contact_conv(self, button):
        """
        Show dialog for adding new contact/conversation.
        :param error_text:
        :return:
        """
        print('blabla')
        conv_name = ''
        for i in self.contacts:
            if i["selected"]:
                i["selected"] = False
                conv_name += i["alias"] + ', '
        if button.get_active():
            # TODO: request do DB s vytvorenim konverzace s uzivateli
            # vypis pridane converzace v aplikaci
            label = Gtk.Label()
            label.set_text(conv_name)
            new_item = Gtk.ListBoxRow()
            new_item.add(label)
            new_item.show_all()
            listbox = self.builder.get_object("conversations_list")
            listbox.add(new_item)
            print('new item ', new_item)
            print('listbox', listbox)
            listbox.connect('row-activated', lambda widget, row: print('hello world'))

    def change_selected(self, name, value):
        for i in self.contacts:
            if i["alias"] == name:
                i["selected"] = value
                print('Selected: ', i["selected"])

    def on_toggle(self, button):
        if button.get_active():
            self.change_selected(button.get_label(), True)
        else:
            self.change_selected(button.get_label(), False)

    def clear_checkbutton_list(self, conversation):
        print('checkbuttony', self.contacts)
        children = conversation.get_children();
        for element in children:
            if element.get_name() == 'GtkCheckButton':
               conversation.remove(element);

    def on_new_conversation_button_pressed(self, arg):
        """
        Add new conversation to conversation list.
        :param error_text:
        :return:
        """
        print('test')
        dialog = self.builder.get_object('dialog_conversation')
        contact_list_conv = self.builder.get_object("conversation_contact_list")
        # nacteni kontaktu do dialogu pro vyber uzivatelu do nove konverzace
        for contact in self.contacts:
            check = Gtk.CheckButton()
            check.set_label(contact["alias"])
            contact_list_conv.add(check)
            check.connect("toggled", self.on_toggle)

        contact_list_conv.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.add_contact_conv(check)
            # contact_list_conv.hide()
            self.clear_checkbutton_list(contact_list_conv)
            dialog.hide()
        elif response == Gtk.ResponseType.CANCEL:
            self.clear_checkbutton_list(contact_list_conv)
            dialog.hide()
        return arg

    def on_add_contact_button_pressed(self, arg):
        """
        Add new contact to contact list.
        :param error_text:
        :return:
        """
        dialog = self.builder.get_object('dialog_contact')
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.add_contact("contact_id_text_input", "contact_name_text_input")
            dialog.hide()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.hide()
        return arg

def run():
    """
    Run application.
    :param error_text:
    :return:
    """
    app = CryptoChat()
    app.__init__()
