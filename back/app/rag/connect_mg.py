import pymongo
from dotenv import load_dotenv
load_dotenv()
import os

def connect_mgs(address):
    if not address:
        raise ValueError("MONGO_URI is not configured")
    myclient = pymongo.MongoClient(address, serverSelectionTimeoutMS=5000)
    mydb = myclient.get_default_database(default="communicate")
    mycol = mydb["rag"]
    return mycol



if __name__ == "__main__":
    mycol = connect_mgs(os.getenv("MONGO_URI"))
    mydict = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydict)
