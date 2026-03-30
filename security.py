import time
from db import tokens, verified, ip_map

EXPIRY = 300  # 5 minutes


# 🔐 Save Token
def save_token(user_id, token):
    tokens.update_one(
        {"user_id": str(user_id)},
        {"$set": {"token": token, "time": time.time()}},
        upsert=True
    )


# 🔍 Check Token
def check_token(user_id, token):
    data = tokens.find_one({"user_id": str(user_id)})

    if not data:
        return "invalid"

    if data.get("token") != token:
        return "wrong token"

    if time.time() - data.get("time", 0) > EXPIRY:
        return "expired"

    return "ok"


# 🌐 Check IP (1 device = 1 ID)
def check_ip(ip, user_id):
    data = ip_map.find_one({"ip": ip})

    if data:
        if str(data.get("user_id")) != str(user_id):
            return False

    return True


# 💾 Save IP mapping
def save_ip(ip, user_id):
    ip_map.update_one(
        {"ip": ip},
        {"$set": {"user_id": str(user_id)}},
        upsert=True
    )


# ✅ Mark Verified
def mark_verified(user_id):
    verified.update_one(
        {"user_id": str(user_id)},
        {"$set": {"status": True, "time": time.time()}},
        upsert=True
    )


# 🔎 Check Verified
def is_verified(user_id):
    return verified.find_one({"user_id": str(user_id)}) is not None


# 🧹 Delete Token (one-time use)
def delete_token(user_id):
    tokens.delete_one({"user_id": str(user_id)})