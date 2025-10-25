# app/database.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")  # set this in your environment or .env
DB_NAME = os.getenv("MONGODB_DB", "zynex_db")

if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI not set. Add it in environment or .env file")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

# Collections
predictions_col = db["predictions"]
suppliers_col = db["suppliers"]

# Helper functions
def save_prediction(record: dict):
    """Save a prediction record (dict) to MongoDB and return inserted id"""
    return predictions_col.insert_one(record).inserted_id

def get_recent_predictions(limit=10):
    return list(predictions_col.find().sort([("_id", -1)]).limit(limit))

def insert_suppliers_if_empty(suppliers_list):
    """Insert suppliers if collection is empty (used at startup)"""
    if suppliers_col.count_documents({}) == 0:
        suppliers_col.insert_many(suppliers_list)

def get_all_suppliers():
    return list(suppliers_col.find({}, {"_id": 0}))
