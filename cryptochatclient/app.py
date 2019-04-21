"""
CryptoChat client main module.
"""
import os
from gi.repository import Gtk
import gi
import random
from urllib.error import HTTPError, URLError

gi.require_version("Gtk", "3.0")
from cryptochatclient.common import *


class CryptoChat(Gtk.Application):
    """
    CryptoChat client GUI class.
    """
    def __init__(self):
        """
        Init.
        """
        self.builder = Gtk.Builder()
        root_dir = os.path.dirname(os.path.abspath(__file__))
        glade_file = os.path.join(root_dir, 'resources/ui/visual.glade')
        self.builder.add_from_file(glade_file)
        self.builder.connect_signals(self)

        self.login_window = self.builder.get_object('login_dialog')
        self.login_window.show_all()

        self.contacts = []
        self.user_id = None
        self.user_password = None
        self.user_private_key = None
        self.user_public_key = None
        self.conversations = dict()
        self.selected_conversation = None

        my_db = DB()
        if my_db.user_exist():
            self.builder.get_object('create_button').set_sensitive(False)
        Gtk.main()

    def on_destroy(self):
        """
        On destroy function.
        """
        Gtk.main_quit()

    def login(self, arg):
        """
        Login function.
        """
        self.login_window = self.builder.get_object('login_dialog')
        login_password = self.builder.get_object("login_password")
        input_password_text = login_password.get_text()
        user = login(input_password_text)
        if user:
            print('Login successful')
            self.user_id = int(user['user_id'])
            self.user_private_key = rsa.PrivateKey.load_pkcs1(user['private_key'].encode('ascii'))
            self.user_public_key = rsa_public_key.load_pkcs1(user['public_key'].encode('ascii'))
            self.login_window.hide()
            self.logged()
        else:
            print('Error')
            self.login_input.set_text('')

    def logged(self):
        """
        Open main window after succesful login.
        """
        self.load_contacts()
        self.load_conversations()
        self.window = self.builder.get_object('main_window')
        self.window.show_all()

    def load_contacts(self):
        """
        Load contacts from the DB.
        """
        contacts_db = get_contacts(self.user_id, self.user_private_key)
        print('contacts: ', contacts_db)
        for contact in contacts_db:
            self.contacts.append({"contact_id": contact['user_id'], "alias": contact['alias'], "selected": False})
            label = Gtk.Label()
            label.set_text(contact['alias'])
            contact_item = self.builder.get_object("contact_list_box")
            contact_item.add(label)
            contact_item.show_all()

    def load_conversations(self):
        """
        Load conversations from the DB.
        """
        conversation_title = ''
        conversation = get_user_chats(self.user_id)
        listbox = self.builder.get_object("conversations_list")

        for conversation in conversation['chats']:
            self.conversations[conversation['id']] = {"user_ids": conversation['users']}
            for user_id in conversation['users']:
                for contact in get_contacts(self.user_id, self.user_private_key):
                    if contact['user_id'] == user_id:
                        if conversation_title == '':
                            conversation_title = conversation_title + str(contact['alias'])
                        else:
                            conversation_title = conversation_title + str(', ' + contact['alias'])
                    label = Gtk.Label()
                    label.set_text(conversation_title)
            conversation_title = ''
            new_item = Gtk.Button()
            new_item.add(label)
            new_item.show_all()
            listbox.add(new_item)
            self.load_sym_key_enc(conversation['id'])
            new_item.connect("clicked", self.on_row_activated, conversation['id'])

    def load_sym_key_enc(self, chat_id):
        """
        Load symetric keys.
        """
        chatinfo = get_chat(chat_id)
        for user, sym_key in zip(chatinfo['users'], chatinfo['sym_key_enc_by_owners_pub_keys']):
            if self.user_id == user:
                self.conversations[chat_id]['sym_key'] = sym_key
                break

    def create_new_user(self, button):
        """
        Create new user according the data in textinputs.
        """
        user_id = self.builder.get_object("login_id")
        user_id_text = user_id.get_text()
        user_password = self.builder.get_object("login_password")
        user_password_text = user_password.get_text()
        self.user_id = int(user_id_text)
        self.user_password = user_password_text
        if user_id_text and user_password_text:
            private_key_owner, public_key_owner = rsa_key_generation()
            private_key_owner_str = private_key_owner.save_pkcs1().decode('ascii')
            public_key_owner_str = public_key_owner.save_pkcs1().decode('ascii')
            save_user_to_db(self.user_id, public_key_owner_str, private_key_owner_str, self.user_password)
            self.user_private_key = private_key_owner
            self.user_public_key = public_key_owner
            print(user_id_text, public_key_owner)
            print('Calling API to create user')
            try:
                create_user(self.user_id, self.user_public_key, self.user_password)
            except (URLError, HTTPError) as e:
                pass
            self.login_window.hide()
            self.logged()

    def on_text_view_set(self, messages):
        """
        Set the messages in chat window.
        """
        text_view = self.builder.get_object("chat_window")
        text_buffer = text_view.get_buffer()
        text_buffer.set_text("")
        end_iter = text_buffer.get_end_iter()
        text_input = self.builder.get_object("message")
        text_input.set_text("")
        for message in messages:
            if message['sender_id'] == self.user_id:
                text_buffer.insert(end_iter, '\n\nMe:\n' + message['message'])
            else:
                for user in get_contacts(self.user_id, self.user_private_key):
                    if user['user_id'] == message['sender_id']:
                        text_buffer.insert(end_iter, '\n' + user['alias'] + ':\n' + message['message'])

    def update_messages(self):
        messages = get_messages(self.selected_conversation,
                                0,
                                self.conversations[self.selected_conversation]['sym_key'],
                                self.user_private_key)
        self.on_text_view_set(messages)

    def on_send_message_button_pressed(self, button):
        """
        Send message.
        """
        input_message = self.builder.get_object("message")
        input_message_text = str(input_message.get_text())
        send_message(self.selected_conversation,
                     self.user_id, input_message_text,
                     self.conversations[self.selected_conversation]['sym_key'],
                     self.user_private_key)
        self.update_messages()

    def contact_enter(self, arg):
        """
        Enter function for adding new contact to contact list.
        """
        self.add_contact("contact_id_text_input", "contact_name_text_input")
        dialog = self.builder.get_object('dialog_contact')
        dialog.hide()

    def add_contact(self, input_id, input_name):
        """
        Show dialog for adding new contact/conversation.
        """
        contact_id = self.builder.get_object(input_id).get_text()
        name = self.builder.get_object(input_name).get_text()
        if name != '' and contact_id != '':
            create_contacts(self.user_id, int(contact_id), name, self.user_public_key)
            self.contacts.append({"contact_id": int(contact_id), "alias": name, "selected": False})
            label = Gtk.Label()
            label.set_text(name)
            contact_item = self.builder.get_object("contact_list_box")
            contact_item.add(label)
            contact_item.show_all()
        self.builder.get_object(input_name).set_text('')
        self.builder.get_object(input_id).set_text('')

    def on_row_activated(self, button, conversation_id):
        """
        Show messages after activated conversation row.
        """
        self.selected_conversation = conversation_id
        self.update_messages()

    def get_updated_messages(self, button):
        """
        Show messages after update button activated.
        """
        self.update_messages()

    def add_contact_conv(self, button):
        """
        Added contacts to created conversations.
        """
        user_ids = [self.user_id]
        conv_name = ''
        for i in self.contacts:
            if i["selected"]:
                user_ids.append(i['contact_id'])
                i["selected"] = False
                conv_name += i["alias"] + ', '

        response = create_chat(user_ids)
        self.conversations[response['chat_id']] = {"user_ids": user_ids}
        self.selected_conversation = response['chat_id']
        label = Gtk.Label()
        label.set_text(conv_name)
        new_item = Gtk.Button()
        new_item.add(label)
        new_item.show_all()
        listbox = self.builder.get_object("conversations_list")
        listbox.add(new_item)
        self.load_sym_key_enc(response['chat_id'])
        new_item.connect("clicked", self.on_row_activated, response['chat_id'])

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
        children = conversation.get_children()
        for element in children:
            if element.get_name() == 'GtkCheckButton':
                conversation.remove(element)

    def on_new_conversation_button_pressed(self, arg):
        """
        Add new conversation to conversation list.
        """
        dialog = self.builder.get_object('dialog_conversation')
        contact_list_conv = self.builder.get_object("conversation_contact_list")
        for contact in self.contacts:
            check = Gtk.CheckButton()
            check.set_label(contact["alias"])
            contact_list_conv.add(check)
            check.connect("toggled", self.on_toggle)

        contact_list_conv.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.add_contact_conv(check)
            self.clear_checkbutton_list(contact_list_conv)
        elif response == Gtk.ResponseType.CANCEL:
            self.clear_checkbutton_list(contact_list_conv)
            dialog.hide()
        self.clear_checkbutton_list(contact_list_conv)
        dialog.hide()
        return arg

    def on_add_contact_button_pressed(self, arg):
        """
        Add new contact to contact list.
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
