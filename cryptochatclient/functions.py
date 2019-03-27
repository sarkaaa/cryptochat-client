import secrets
from builtins import print

import rsa
import sha3
from Crypto.Cipher import AES


def rsa_key_generation():
    print("Please wait a few minutes. Application generates secure keys ... ")
    (public_key_owner, private_key_owner) = rsa.newkeys(4096, poolsize=8)
    return private_key_owner, public_key_owner


def rsa_encryption(public_key_of_receiver, block_bits):  ##################### sifrovani s public key prijemcu
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


def random_generator_key(size_of_key):
    random_number = secrets.randbelow(30000000000000000)  ########len tak teraz neries

    k = sha3.keccak_512()
    k.update(bytes(random_number))

    return k.hexdigest()


def encryption(message_block, key, IV):
    ############################### encryption message from transceiver ###################################
    message_block_size = len(message_block)  # size Byte of message_block
    message = ""  # blok 16Byte
    array_ciphertext = []
    x = -1  # pomocna pro urceni velkostio bloku, protoze umi zasifrovat len 16Byte naraz

    for i in range(0, len(message_block)):  # cyklus od 0 po velkost spravy
        message += message_block[i]  # pripocitam aktualny ynak z spravy
        x += 1
        if x == 13:  # urci nam velkost bloku na 14Byte lebo pridame +2Byte zahlavi
            x = -1  # vynuluje promenu
            message += "02"  # zahlavi
            obj = AES.new(key, AES.MODE_CBC, IV)  # vytvori tzv. sifrer AES
            ciphertext = obj.encrypt(message)  # zasifruje message
            array_ciphertext.append(ciphertext)  # prida tento blok do pola
            IV = ciphertext  # IV sa stane predchadzajuca zasifrovana sprava princip CBC modu
            message = ""  # vynuluje message
        if i == (len(message_block) - 1):  # ked je posledny znak
            residue_value = ((i + 1) % 14)  # pocet znaku v poslednem bloku, aby sme vedeli dat vypln
            cycle = 16 - residue_value  # pocet Bytu vyplne neskur pouzijeme jak pocet nahodnych znaku
            value_cycle = cycle  # pocet Bytu vyplne
            if residue_value != 0:  # podminka ze by posledny blok byl presne 14
                if cycle < 10:  # ked sa bude doplnat menej jak 10 bytu tak aby sme pridali max 8xnahodny znak a na max konec 9 jedno misto na vyjadreni kolko ich je
                    cycle -= 1  # pocet nahodnych znaku
                else:  # ked doplname 10 az 15 tak aby bylo max 13x nahodny znak a max15 na konci dve mista na vyjadreni kolko ich je
                    cycle -= 2  # pocet 0

                for i in range(0, cycle):  # cyklus na pridani nahodnych znaku
                    message += str(secrets.randbelow(10))  # pridani nahodnych znaku
                message += str(value_cycle)  # pridani kolko je vyplne
                obj = AES.new(key, AES.MODE_CBC, IV)
                ciphertext = obj.encrypt(message)
                array_ciphertext.append(ciphertext)
                IV = ciphertext

    return array_ciphertext


def decryption(array_ciphertext, key, IV):
    ######################## decryption message for receiver #######################################

    plaintext = ""

    for i in range(0, len(array_ciphertext)):  # cyklus od 0 do poctu sifrovanych bloku
        message = array_ciphertext[i]  # jeden blok
        obj = AES.new(key, AES.MODE_CBC, IV)
        plaintext_with_payload = obj.decrypt(message)  # desifrovani bloku
        IV = message  # zmenime IV kvuli CBC modu
        value = int(chr(plaintext_with_payload[14])) * 10 + int(
            chr(plaintext_with_payload[15]))  # zistime pocet vyplne z poslednych 2 Byte

        chars_of_message = 16 - value  # pocet znaku bez vyplne
        for j in range(0, chars_of_message):
            plaintext += chr(plaintext_with_payload[j])  # prepisujeme znaky bez vyplne

    return plaintext
