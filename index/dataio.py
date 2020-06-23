import pymongo

class DataIO:

    def __init__(self, uri):
        self.client = pymongo.MongoClient(uri)
        self.database = self.client.get_database("discord-bot")

    def fetch_all(self, col_name):
        col = self.database.get_collection(col_name)
        return col.find({})

    def fetch(self, col_name, id):
        col = self.database.get_collection(col_name)
        return col.find_one({"id": id})

    def delete(self, col_name, id):
        col = self.database.get_collection(col_name)
        return col.find_one_and_delete({"id": id})

    def update(self, col_name, doc):
        col = self.database.get_collection(col_name)
        return col.find_one_and_replace({"id": doc["id"]}, doc)

    def insert(self, col_name, doc):
        col = self.database.get_collection(col_name)
        return col.insert(doc)