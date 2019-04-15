"""
Module to handle database calls.
"""

import json
from tinydb import Query, where, TinyDB



class DB:
    """
    Database class for handling the database queries
    """

    def __init__(self):
        self.db = TinyDB('./data.json')
        self.query = Query()

    def createUser(self, id, publicKey, privateKey):
        self.db.insert({"type": "account","id": id, "publicKey": publicKey, "privateKey": privateKey})

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



if __name__ == "__main__":

    print("Start")

    db = DB()
    #db.createUser(123456, 55555555,66666666)

    print(db.selectUser()[0])

    print(db.getID())
    print(db.getPublicKey())
    print(db.getPrivateKey())