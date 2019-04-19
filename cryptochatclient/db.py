"""
Module to handle database calls.
"""

import json
import os
from tinydb import Query, where, TinyDB


def _get_default_db_path():
    project_root = os.path.dirname(os.path.abspath(__file__))
    full_path = project_root + '/../.data/db.json'
    return full_path


class DB:
    """
    Database class for handling the database queries
    """

    def __init__(self):
        self.db = TinyDB(_get_default_db_path())
        self.query = Query()

    def createUser(self, id, publicKey, privateKey, password_hash):
        self.db.insert({"type": "account",
                        "id": id,
                        "publicKey": publicKey,
                        "privateKey": privateKey,
                        "password_hash": password_hash})

    def selectUser(self):
        query = Query()
        return self.db.search(query.type == 'account')

    def getID(self):
        data = json.dumps(self.selectUser()[0])
        dataString = json.loads(data)

        return dataString['id']

    def getPublicKey(self):
        data = json.dumps(self.selectUser()[0])
        dataString = json.loads(data)
        return dataString['publicKey']

    def getPrivateKey(self):
        data = json.dumps(self.selectUser()[0])
        dataString = json.loads(data)
        return dataString['privateKey']

    def get_password_hash(self):
        data = json.dumps(self.selectUser()[0])
        dataString = json.loads(data)
        return dataString['password_hash']

    def user_exist(self):
        if not self.selectUser():
            return False
        return True

if __name__ == "__main__":

    print("Start")

    db = DB()
    db.createUser(123456, 55555555,66666666, 'hash')

    print(db.selectUser()[0])

    print(db.getID())
    print(db.getPublicKey())
    print(db.getPrivateKey())
    print(db.get_password_hash())