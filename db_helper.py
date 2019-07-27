# Database Helper 
# Performs all database related function
import os
import uuid
import json
import pymongo
from datetime import datetime
from bson.json_util import dumps

class DatabaseHelper(object):
    def validateCredentials(self, email, password):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = client["cloud"]
        collection = database["users"]
        user = collection.count({"email": email, "password": password})
        # if the credentials do not exist in the database return false
        # else return a uuid header to allow the user to upload their file
        if user == 1:
            token = str(uuid.uuid4())
            # setting token
            collection.update_one({"email": email, "password": password}, {"$set": {"token": token}})
            return token
        else: 
            return None

    def validateToken(self, token):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = client["cloud"]
        collection = database["users"]
        token_match = collection.count({"token": token})
        if token_match ==  1:
            return True
        else:
            return False

    def removeToken(self, token):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = client["cloud"]
        collection = database["users"]
        collection.update_one({"token": token}, {"$set": {"token": ""}})
        return True

    def addFileToList(self, fname, token):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = client["cloud"]
        collection = database["users"]
        collection.update_one({"token": token}, {"$addToSet": {"files": {"name": fname, "dateUploaded": str(datetime.today().replace(microsecond=0)), "size": os.path.getsize(os.getcwd()+"\\uploads\\"+fname)}}})
    
    def fetchAllFiles(self, token):
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        database = client["cloud"]
        collection = database["users"]
        files = json.dumps(dumps(collection.find({"token": token}, {"files": 1, "_id": 0}))[1:-1])
        return files