import base64
import hashlib
import json
from builtins import print
from urllib import request

import rsa
from Crypto import Random
from Crypto.Cipher import AES

from cryptochatclient.logging_utils import get_logger

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
    return signature, block_bits.encode('utf8')


def rsa_verification(public_key_of_receiver, signature, block_bits):
    boolean_value = rsa.verify(block_bits, signature, public_key_of_receiver)
    if boolean_value:
        print("podpis sedi, sprava nebyla zmenena")
    else:
        print("chybny podpis")
    return boolean_value, block_bits.decode('utf8')


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
    LOGGER.debug('Executing GET request to endpoint "%s" ).', full_endpoint)
    resp_get = request.urlopen(req).read()
    resp_get_json = json.loads(resp_get)
    LOGGER.debug('Received response: %s', str(resp_get_json))
    return resp_get_json


def make_post_request(endpoint, data):
    data = prepare_request_data(data)
    full_endpoint = 'http://localhost:8888' + endpoint
    req = request.Request(full_endpoint,
                          data=data,
                          method='POST')
    LOGGER.debug('Executing POST request to endpoint "%s" ).', full_endpoint)
    resp_post = request.urlopen(req).read()
    resp_post_json = json.loads(resp_post)
    LOGGER.debug('Received response: %s', str(resp_post_json))
    return resp_post_json


def send_message(chat_id, owner_id, message,
                 symmetric_key_encrypted_by_own_pub_key, owner_private_key):
    key = rsa_decryption(owner_private_key, symmetric_key_encrypted_by_own_pub_key)
    encrypted_message = encryption(message, key)

    data_post = {'chat_id': int(chat_id),
                 'sender_id': int(owner_id),
                 'message': str(encrypted_message)}
    resp_post_json = make_post_request('/api/message/new', data_post)
    return resp_post_json


def get_messages(chat_id, cursor):  # cursor is float
    data_post = {'chat_id': int(chat_id),
                 'cursor': cursor
                 }

    # TODO: complete this

    resp_post_json = make_post_request('/api/message/new', data_post)
    return resp_post_json['messages']


def create_contacts(owner_id, user_id, alias, owner_pub_key):
    encrypted_alias = rsa_encryption(owner_pub_key, alias)

    data_post = {'owner_id': int(owner_id),
                 'user_id': int(user_id),
                 'encrypted_alias': str(encrypted_alias)}
    resp_post_json = make_post_request('/api/contacts', data_post)
    return resp_post_json


def get_contacts(owner_id):
    data_get = {'owner_id': owner_id}
    resp_get_json = make_get_request('/api/contacts', data_get)
    return resp_get_json['contacts']


def create_user(owner_id, owner_pub_key):
    # TODO: not a good idea to cast public key to string
    data_post = {'user_id': int(owner_id), 'public_key': str(owner_pub_key)}
    resp_post_json = make_post_request('/api/users', data_post)
    return resp_post_json


def get_user(user_id):
    data_get = {'user_id': user_id}
    resp_get_json = make_get_request('/api/users', data_get)
    return resp_get_json


def create_chat(user_ids, key):
    key = str(key).encode('utf-8')
    key = hashlib.sha256(key).digest()

    sym_key_enc_by_owners_pub_keys = []
    for i in range(0, len(user_ids)):
        user_id = user_ids[i]
        user = get_user(user_id)
        public_key = user.get('public_key')
        print(public_key)
        sym_key_enc_by_owners_pub_keys.append(rsa_encryption(public_key, key))

    # TODO: fix data input to api
    data_post = {'users': int(user_ids),
                 'sym_key_enc_by_owners_pub_keys': str(sym_key_enc_by_owners_pub_keys)}
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

    key = hashlib.sha256(key.encode()).digest()
    enc = base64.b64decode(array_ciphertext)
    encrypt_iv = enc[:AES.block_size]
    cipher_iv = AES.new(key, AES.MODE_ECB)
    iv = cipher_iv.decrypt(encrypt_iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    text = _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')
    return text
