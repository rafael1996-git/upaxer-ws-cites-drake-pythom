from pymongo import MongoClient
import os
from common.Secret import get_secret
from bson import DBRef, ObjectId


class MongoPool:
    def __init__(self):

        self.db_info = get_secret(os.environ['SECRET_MONGO'])
        self.server = self.db_info['host']
        self.port = self.db_info['port']
        self.user = self.db_info['username']
        self.password = self.db_info['password']
        self.database = self.db_info['database']
        conn = MongoClient(
            self.server,
            username=self.user,
            password=self.password,
            authSource=self.database
        )
        self.client = conn['upaxer-db']

    def find(self, collection, params):
        try:
            data = self.client[collection].find(params)
            lstData = list()
            for d in data:
                lstData.append(d)
            return lstData
        except Exception as e:
            raise Exception({'message': 'Error de conexión con MongoDB', 'code': 'UPX601'})

    def insert_one(self, collection, data):
        try:
            result = self.client[collection].insert_one(data).inserted_id
            return result
        except Exception as e:
            raise Exception({'message': 'Error de conexión con MongoDB', 'code': 'UPX601'})

    def insert_many(self, collection, data):
        try:
            result = [str(ids) for ids in self.client[collection].insert_many(data, ordered=False).inserted_ids]
            return result
        except Exception as e:
            raise Exception({'message': 'Error de conexión con MongoDB', 'code': 'UPX601'})

    def update_many(self, collection, lstData, filter):
        try:
            lstUpdate = list()
            for data in lstData:
                #id = filter['_id']
                if '_id' in data:
                    del data['_id']
                #result = self.client[collection].replace_one({"_id": ObjectId(id)},
                                                             #filter, upsert=True)
                result = self.client[collection].replace_one({filter: data[filter]},
                                                                         data, upsert=True)
                filterU = {"_id": id,
                         "modidied": result.modified_count}
                lstUpdate.append(filterU)

            return lstUpdate
        except Exception as e:
            raise Exception({'message': 'Error de conexión con MongoDB', 'code': 'UPX601'})

    def delete_many(self, collection, lstData, filter):
        try:
            #result = self.client[collection].remove({'_id': {'$in': lstFilter}})
            result = self.client[collection].remove({filter: {'$in': lstData}})
            return result
        except Exception as e:
            raise Exception({'message': 'Error de conexión con MongoDB', 'code': 'UPX601'})
