from pymongo import MongoClient

MONGO_URL = "YOUR_MONGO_URL"

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["nexa"]

tokens = db["tokens"]
verified = db["verified"]
ip_map = db["ip_map"]


# ⚡ Create Indexes (IMPORTANT for speed)
tokens.create_index("user_id")
verified.create_index("user_id")
ip_map.create_index("ip")