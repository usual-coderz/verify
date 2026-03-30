import time
from db import tokens, verified, ip_map

EXPIRY = 300  # 5 min


def save_token(user_id, token):
    tokens.update_one(
        {"user_id": user_id},
        {"$set": {"token": token, "time": time.time()}},
        upsert=True
    )


def check_token(user_id, token):
    data = tokens.find_one({"user_id": user_id})

    if not data:
        return "invalid"

    if data["token"] != token:
        return "wrong token"

    if time.time() - data["time"] > EXPIRY:
        return "expired"

    return "ok"


def check_ip(ip, user_id):
    data = ip_map.find_one({"ip": ip})

    if data and data["user_id"] != user_id:
        return False

    return True


def save_ip(ip, user_id):
    ip_map.update_one(
        {"ip": ip},
        {"$set": {"user_id": user_id}},
        upsert=True
    )


def mark_verified(user_id):
    verified.update_one(
        {"user_id": user_id},
        {"$set": {"status": True}},
        upsert=True
    )


def is_verified(user_id):
    return verified.find_one({"user_id": user_id}) is not None


def delete_token(user_id):
    tokens.delete_one({"user_id": user_id})