from flask import Flask, request, jsonify, render_template
from security import *
import os

app = Flask(__name__)

BOT_USERNAME = "YourBotUsername"


def get_ip():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr


@app.route("/")
def home():
    user_id = request.args.get("user_id")
    token = request.args.get("token")

    return render_template(
        "index.html",
        user_id=user_id,
        token=token,
        bot=BOT_USERNAME
    )


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    save_token(str(data["user_id"]), data["token"])
    return jsonify({"status": "ok"})


@app.route("/verify")
def verify():
    user_id = request.args.get("user_id")
    token = request.args.get("token")

    ip = get_ip()

    # 🔐 IP restriction
    if not check_ip(ip, user_id):
        return jsonify({"status": "❌ One device = one account only!"})

    # 🔐 Token check
    status = check_token(user_id, token)
    if status != "ok":
        return jsonify({"status": status})

    # ✅ Save IP
    save_ip(ip, user_id)

    # ✅ Mark verified
    mark_verified(user_id)

    # 🧹 delete token
    delete_token(user_id)

    return jsonify({"status": "verified"})


@app.route("/check")
def check():
    user_id = request.args.get("user_id")
    return jsonify({"verified": is_verified(user_id)})


app.run(host="0.0.0.0", port=5000)