from pymongo import MongoClient

MONGO_URL = "YOUR_MONGO_URL"

client = MongoClient(MONGO_URL)
db = client["nexa"]

tokens = db["tokens"]       # store tokens
verified = db["verified"]  # verified users
ip_map = db["ip_map"]      # ip → user mapping