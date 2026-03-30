from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL") or "YOUR_MONGO_URL"

client = MongoClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000
)

db = client["nexa"]

tokens = db["tokens"]
verified = db["verified"]
ip_map = db["ip_map"]


# ⚡ Indexes
tokens.create_index("user_id")
verified.create_index("user_id")
ip_map.create_index("ip")

# 🔥 TTL Index (Auto delete after 5 min)
tokens.create_index("time", expireAfterSeconds=300)