import base64
import hashlib
import json
from builtins import print
from secrets import token_bytes
from urllib import request

import rsa
from Crypto import Random
from Crypto.Cipher import AES
from rsa.key import PublicKey as rsa_public_key
from rsa.transform import bytes2int, int2bytes

from cryptochatclient.logging_utils import get_logger
from cryptochatclient.db import DB

LOGGER = get_logger(__name__)


################## Variable in client aplication ##################


# owner_ID = 1518423168121484512158
# owner_pub_key = ""
# owner_private_key = ""


###################################################################


def rsa_key_generation():
    print("Please wait a few minutes. Application generates secure keys ... ")
    (public_key_owner, private_key_owner) = rsa.newkeys(2048, poolsize=8)
    return private_key_owner, public_key_owner


def rsa_encryption(public_key_of_receiver, block_bits):
    """
    Sifrovani s public key prijemcu
    :param public_key_of_receiver:
    :param block_bits:
    :return:
    """
    message = block_bits.encode('utf8')  # dekodovani
    ciphertext = rsa.encrypt(message, public_key_of_receiver)  # zasifrovani pomocu public key

    return ciphertext


def rsa_decryption(private_key_of_owner, ciphertext):
    message = rsa.decrypt(ciphertext, private_key_of_owner)
    message.decode('utf8')

    return message


def rsa_signing(private_key_of_owner, block_bits):
    signature = rsa.sign(block_bits.encode('utf8'), private_key_of_owner, 'SHA-512')

    return signature


def rsa_verification(public_key_of_receiver, signature, block_bits):
    boolean_value = rsa.verify(block_bits, signature, public_key_of_receiver)
    if boolean_value:
        return True
    else:
        return False


def encryption(message_block, key):
    bs = 32
    key = hashlib.sha256(key).digest()

    def _pad(s):
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    raw = _pad(message_block)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_iv = AES.new(key, AES.MODE_ECB)
    array_ciphertext = base64.b64encode(cipher_iv.encrypt(iv) + cipher.encrypt(raw))

    return array_ciphertext


def prepare_request_data(data):
    # Dict to Json
    data_post = json.dumps(data)
    # Convert to String
    data_post = str(data_post)
    # Convert string to byte
    data_post = data_post.encode('utf-8')

    return data_post


def make_get_request(endpoint, data):
    data = prepare_request_data(data)
    full_endpoint = 'http://localhost:8888' + endpoint
    req = request.Request(full_endpoint,
                          data=data,
                          method='GET')
    LOGGER.info('Executing GET request to endpoint "%s".', full_endpoint)
    resp_get = request.urlopen(req).read()
    resp_get_json = json.loads(resp_get)
    LOGGER.info('Received response: %s', str(resp_get_json))

    return resp_get_json


def make_post_request(endpoint, data):
    data = prepare_request_data(data)
    full_endpoint = 'http://localhost:8888' + endpoint
    req = request.Request(full_endpoint,
                          data=data,
                          method='POST')
    LOGGER.info('Executing POST request to endpoint "%s".', full_endpoint)
    resp_post = request.urlopen(req).read()
    resp_post_json = json.loads(resp_post)
    LOGGER.info('Received response: "%s"', str(resp_post_json))

    return resp_post_json


def send_message(chat_id, sender_id, message,
                 symmetric_key_encrypted_by_own_pub_key, owner_private_key):
    symmetric_key_encrypted_by_own_pub_key = int2bytes(int(symmetric_key_encrypted_by_own_pub_key))

    key = rsa_decryption(owner_private_key, symmetric_key_encrypted_by_own_pub_key)
    encrypted_message = encryption(message, key)
    encrypted_message = bytes2int(encrypted_message)

    hash = hashlib.sha256((str(chat_id) + str(sender_id) + str(encrypted_message)).encode()).hexdigest()

    signedHash = bytes2int(rsa_signing(owner_private_key, hash))

    data_post = {'chat_id': int(chat_id),
                 'sender_id': int(sender_id),
                 'message': str(encrypted_message),
                 'hash': signedHash}
    resp_post_json = make_post_request('/api/message/new', data_post)

    return resp_post_json


def get_messages(chat_id, cursor,
                 symmetric_key_encrypted_by_own_pub_key,
                 owner_private_key):  # cursor is float
    data_post = {'chat_id': int(chat_id),
                 'cursor': cursor
                 }
    resp_post_json = make_post_request('/api/message/updates', data_post)

    symmetric_key_encrypted_by_own_pub_key = int2bytes(int(symmetric_key_encrypted_by_own_pub_key))
    key = rsa_decryption(owner_private_key, symmetric_key_encrypted_by_own_pub_key)
    for get_message in resp_post_json['messages']:
        message = int2bytes(int(get_message['message']))
        decrypted_message = decryption(message, key)
        get_message['message'] = decrypted_message

    return resp_post_json['messages']


def create_contacts(owner_id, user_id, alias, owner_pub_key):
    encrypted_alias = rsa_encryption(owner_pub_key, alias)
    encrypted_alias = bytes2int(encrypted_alias)

    data_post = {'owner_id': int(owner_id),
                 'user_id': int(user_id),
                 'encrypted_alias': str(encrypted_alias)}
    resp_post_json = make_post_request('/api/contacts', data_post)

    return resp_post_json


def get_contacts(owner_id, owner_priv_key):
    data_get = {'owner_id': int(owner_id)}
    resp_get_json = make_get_request('/api/contacts', data_get)

    for contact in resp_get_json['contacts']:
        alias = int2bytes(int(contact['alias']))
        contact['alias'] = rsa_decryption(owner_priv_key, alias).decode()

    return resp_get_json['contacts']


def create_user(owner_id, owner_pub_key, password):
    hash_pasword = hashlib.sha256(password.encode()).digest()  # TODO: Save this to cache
    owner_pub_key = owner_pub_key.save_pkcs1().decode('ascii')

    data_post = {'user_id': int(owner_id), 'public_key': owner_pub_key}
    resp_post_json = make_post_request('/api/users', data_post)

    return resp_post_json


def get_user(user_id):
    data_get = {'user_id': user_id}
    resp_get_json = make_get_request('/api/users', data_get)

    return resp_get_json


def create_chat(user_ids):
    key = token_bytes(32)
    key = hashlib.sha256(key).hexdigest()

    sym_key_enc_by_owners_pub_keys = []
    for i in range(0, len(user_ids)):
        user_id = user_ids[i]
        user = get_user(user_id)
        public_key = user.get('public_key')
        public_key = rsa_public_key.load_pkcs1(public_key)
        print(public_key)
        enc_sym_key = bytes2int(rsa_encryption(public_key, key))
        sym_key_enc_by_owners_pub_keys.append(str(enc_sym_key))

    # TODO: fix data input to api
    data_post = {'users': user_ids,
                 'sym_key_enc_by_owners_pub_keys': sym_key_enc_by_owners_pub_keys}
    resp_post_json = make_post_request('/api/chats', data_post)

    return resp_post_json


def get_chat(chat_id):
    data_get = {'chat_id': chat_id}
    resp_get_json = make_get_request('/api/chats', data_get)

    return resp_get_json


def get_user_chats(user_id):
    data_get = {'user_id': user_id}
    resp_get_json = make_get_request('/api/chats/user', data_get)

    return resp_get_json


def decryption(array_ciphertext, key):
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    key = hashlib.sha256(key).digest()
    enc = base64.b64decode(array_ciphertext)
    encrypt_iv = enc[:AES.block_size]
    cipher_iv = AES.new(key, AES.MODE_ECB)
    iv = cipher_iv.decrypt(encrypt_iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    text = _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    return text

def login(password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    my_db = DB()
    hash_password = my_db.get_password_hash()

    if password_hash == hash_password:
        print('heslo je spravne')
        user = dict()
        user['user_id'] = my_db.getID()
        user['public_key'] = my_db.getPublicKey()
        user['private_key'] = my_db.getPrivateKey()
        return user
    else:
        print('neplatne heslo')
        return False


def save_user_to_db(user_id, public_key, private_key, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    my_db = DB()
    my_db.createUser(user_id, public_key, private_key, password_hash)


if __name__ == '__main__':
    PRIVATE_KEY_USER1, PUBLIC_KEY_USER1 = rsa_key_generation()
    PRIVATE_KEY_USER2, PUBLIC_KEY_USER2 = rsa_key_generation()

    USER1 = {'user_id': 123,
             'public_key': PUBLIC_KEY_USER1,
             'private_key': PRIVATE_KEY_USER1,
             'password': 'password123'}
    USER2 = {'user_id': 123456,
             'public_key': PUBLIC_KEY_USER2,
             'private_key': PRIVATE_KEY_USER2,
             'password': 'password321'}
    USERS = [USER1, USER2]
    CONTACT1 = {'owner_id': USER1.get('user_id'),
                'user_id': USER2.get('user_id'),
                'contact_alias': 'USER2 in contacts of USER1'}
    CONTACT2 = {'owner_id': USER2.get('user_id'),
                'user_id': USER1.get('user_id'),
                'contact_alias': 'USER1 in contacts of USER2'}
    CHAT1 = {'users': [USER1.get('user_id'), USER2.get('user_id')]}
    MESSAGES = [{'chat_id': None,
                 'sender_id': CHAT1.get('users')[0],
                 'message': "Hi there!"},
                {'chat_id': None,
                 'sender_id': CHAT1.get('users')[1],
                 'message': 'Oh hi! I have some news for you!'},
                {'chat_id': None,
                 'sender_id': CHAT1.get('users')[0],
                 'message': 'I am curious, tell me...'},
                {'chat_id': None,
                 'sender_id': CHAT1.get('users')[1],
                 'message': 'We are not real... :-('}
                ]

    create_user(USER1.get('user_id'), USER1.get('public_key'), USER1.get('password'))
    create_user(USER2.get('user_id'), USER2.get('public_key'), USER2.get('password'))

    GET_USER2 = get_user(USER2.get('user_id'))
    print(GET_USER2)
    ASSERTION = GET_USER2.get('user_id') == USER2.get('user_id') and \
                rsa.PublicKey.load_pkcs1(GET_USER2.get('public_key')) \
                == USER2.get('public_key')
    assert ASSERTION

    create_contacts(CONTACT1.get('owner_id'),
                    CONTACT1.get('user_id'),
                    CONTACT1.get('contact_alias'),
                    USER1.get('public_key'))
    create_contacts(CONTACT2.get('owner_id'),
                    CONTACT2.get('user_id'),
                    CONTACT2.get('contact_alias'),
                    USER2.get('public_key'))

    RESULT = get_contacts(USER2.get('user_id'), USER2.get('private_key'))
    print(RESULT[0])
    assert RESULT[0]['owner_id'] == USER2['user_id']
    assert RESULT[0]['user_id'] == USER1['user_id']
    assert RESULT[0]['alias'] == CONTACT2['contact_alias']

    create_chat(CHAT1.get('users'))

    GET_USER_CHATS = get_user_chats(USER1.get('user_id'))
    USER_FIRST_CHAT = GET_USER_CHATS['chats'][0]
    GET_CHAT1 = get_chat(USER_FIRST_CHAT.get('id'))
    ASSERTION = GET_CHAT1.get('chat_id') == USER_FIRST_CHAT.get('id') and \
                GET_CHAT1.get('users') == USER_FIRST_CHAT.get('users') and \
                GET_CHAT1.get('sym_key_enc_by_owners_pub_keys') == \
                USER_FIRST_CHAT.get('sym_key_enc_by_owners_pub_keys')
    assert ASSERTION

    for message in MESSAGES:
        message['chat_id'] = GET_CHAT1['chat_id']
        for user, sym_key in zip(GET_CHAT1['users'], GET_CHAT1['sym_key_enc_by_owners_pub_keys']):
            if message['sender_id'] == user:
                message['sym_key_enc'] = sym_key
        for user in USERS:
            if message['sender_id'] == user['user_id']:
                message['owner_private_key'] = user['private_key']

    SENT_MESSAGES = []
    for it_message in MESSAGES:
        SENT_MESSAGES.append(send_message(it_message.get('chat_id'),
                                          it_message.get('sender_id'),
                                          it_message.get('message'),
                                          it_message.get('sym_key_enc'),
                                          it_message.get('owner_private_key')))

    RESULT = get_messages(GET_CHAT1.get('chat_id'),
                          SENT_MESSAGES[0]['timestamp'],
                          GET_CHAT1['sym_key_enc_by_owners_pub_keys'][0],
                          USER1['private_key'])
    RESULT.sort(key=lambda x: x.get('timestamp'))

    for idx, it_message in enumerate(RESULT):
        assert it_message.get('chat_id') == MESSAGES[idx + 1].get('chat_id')
        assert it_message.get('sender_id') == MESSAGES[idx + 1].get('sender_id')
        assert it_message.get('message') == MESSAGES[idx + 1].get('message')
