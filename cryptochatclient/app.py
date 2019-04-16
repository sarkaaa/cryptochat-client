"""
CryptoChat client main module.
"""
import os
from gi.repository import Gtk
import gi
gi.require_version("Gtk", "3.0")
from cryptochatclient.common import *

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

        self.user_id = None
        self.user_private_key = None
        self.user_public_key = None

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

    def create_new_user(self, button):
        user_id = self.builder.get_object("login_id")
        user_id_text = user_id.get_text()
        self.user_id = user_id_text
        if user_id_text:
            private_key_owner, public_key_owner = rsa_key_generation()
            self.user_private_key = private_key_owner
            self.user_public_key = public_key_owner
            print(user_id_text, public_key_owner)
            print('Calling API to create user')
            create_user(self.user_id, self.user_public_key)
            self.login_window.hide()
            self.logged()

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
            # TODO: pridat kontakty taky do self promenne
            create_contacts(self.user_id, int(contact_id), name, self.user_public_key)
            # vypis pridaneho uzivatele v aplikaci
            label = Gtk.Label()
            label.set_text(name)
            contact_item = self.builder.get_object("contact_list_box")
            contact_item.add(label)
            contact_item.show_all()
        self.builder.get_object(input_name).set_text('')
        self.builder.get_object(input_id).set_text('')

    def on_row_activated(self, listbox, row):
        """
        Show dialog for adding new contact/conversation.
        :param error_text:
        :return:
        """
        print("ahhoooj")

    def add_contact_conv(self, button, conv):
        """
        Show dialog for adding new contact/conversation.
        :param error_text:
        :return:
        """
        dialog = self.builder.get_object('dialog_conversation')
        if button.get_active():
            # TODO: request do DB s vytvorenim konverzace s uzivateli
            # vypis pridane converzace v aplikaci
            label = Gtk.Label()
            label.set_text(conv)
            new_item = Gtk.ListBoxRow()
            new_item.add(label)
            new_item.show_all()
            listbox = self.builder.get_object("conversations_list")
            listbox.add(new_item)
            listbox.connect('row-activated', self.on_row_activated)

    def on_new_conversation_button_pressed(self, arg):
        """
        Add new conversation to conversation list.
        :param error_text:
        :return:
        """
        dialog = self.builder.get_object('dialog_conversation')
        contact_list_conv = self.builder.get_object("conversation_contact_list")
        # nacteni kontaktu do dialogu pro vyber uzivatelu do nove konverzace
        user_list = ['Roland', 'Sarka', 'Roman', 'Ondra']
        for i in range(0, len(user_list)):
            check = Gtk.CheckButton()
            check.set_label(user_list[i])
            contact_list_conv.add(check)

        conv_name = ', '.join(user_list)
        contact_list_conv.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            check.connect("toggled", self.add_contact_conv)
            self.add_contact_conv(check, conv_name)
            contact_list_conv.hide()
            dialog.hide()
        elif response == Gtk.ResponseType.CANCEL:
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
    
    def test_test(self):
        print('ahoooj')

def run():
    """
    Run application.
    :param error_text:
    :return:
    """
    app = CryptoChat()
    app.__init__()
