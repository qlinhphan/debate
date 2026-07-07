import pymongo
from dotenv import load_dotenv
load_dotenv()
import os

def connect_mgs(address):
    myclient = pymongo.MongoClient(address)
    mydb = myclient["db"]
    mycol = mydb["rag"]
    return mycol



if __name__ == "__main__":
    mycol = connect_mgs(os.getenv("MONGO_URI"))
    mydict = { "name": "John", "address": "Highway 37" }
    x = mycol.insert_one(mydict)