import os

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


MONGO_URI = (os.getenv("MONGO_URI") or "").strip()
DATABASE_NAME = (os.getenv("DATABASE_NAME") or "hybrid_ecommerce").strip()


if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from .env or environment variables")

if not DATABASE_NAME:
    raise ValueError("DATABASE_NAME is missing from .env or environment variables")


client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

db = client[DATABASE_NAME]


users_collection = db["users"]
products_collection = db["products"]
reviews_collection = db["reviews"]
interactions_collection = db["interactions"]
carts_collection = db["carts"]
wishlists_collection = db["wishlists"]
orders_collection = db["orders"]