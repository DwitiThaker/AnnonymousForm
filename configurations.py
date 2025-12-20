from pymongo import MongoClient #type: ignore
from pymongo.server_api import ServerApi  # type: ignore
from pymongo.collection import Collection  #type: ignore
from dotenv import load_dotenv
load_dotenv()



uri = "mongodb+srv://dbu_user:kx3o7cOfBrn9Fpr1@cluster0.wq2ppde.mongodb.net/db-form-dev"

client = MongoClient(uri, server_api=ServerApi('1'))
import os






db = client.form_db

user_collection: Collection = db["user"]
admin_collection: Collection = db["admin"]
form_collection: Collection = db["forms"]  
response_collection: Collection = db['response']
access_code_batch_collection: Collection = db['code_batch']



def get_user_collection() -> Collection:
    return user_collection 

def get_admin_collection() -> Collection:
    return admin_collection

def get_form_collection() -> Collection:
    return form_collection

def get_response_collection() -> Collection:
    return response_collection

def get_access_code_batch_collection() -> Collection:
    return access_code_batch_collection


