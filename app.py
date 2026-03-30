from flask import Flask, request, jsonify, render_template
from security import (
    save_token,
    check_token,
    check_ip,
    save_ip,
    mark_verified,
    is_verified,
    delete_token
)

app = Flask(__name__)

BOT_USERNAME = "YourBotUsername"


# 🌐 Get real client IP (proxy safe)
def get_ip():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if ip:
        ip = ip.split(",")[0].strip()
    return ip


# 🏠 Home Page
@app.route("/")
def home():
    user_id = request.args.get("user_id")
    token = request.args.get("token")

    # basic validation
    if not user_id or not token:
        return "Invalid Request", 400

    return render_template(
        "index.html",
        user_id=user_id,
        token=token,
        bot=BOT_USERNAME
    )


# 🔐 Generate Token (called by bot)
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    if not data or "user_id" not in data or "token" not in data:
        return jsonify({"status": "invalid request"}), 400

    user_id = str(data["user_id"])
    token = data["token"]

    save_token(user_id, token)

    return jsonify({"status": "ok"})


# ✅ Verify User
@app.route("/verify")
def verify():
    user_id = request.args.get("user_id")
    token = request.args.get("token")

    # input validation
    if not user_id or not token:
        return jsonify({"status": "invalid request"})

    ip = get_ip()

    # 🔐 IP restriction
    if not check_ip(ip, user_id):
        return jsonify({"status": "❌ One device = one account only!"})

    # 🔐 Token validation
    status = check_token(user_id, token)
    if status != "ok":
        return jsonify({"status": status})

    # ✅ Save IP mapping
    save_ip(ip, user_id)

    # ✅ Mark verified
    mark_verified(user_id)

    # 🧹 Delete token (one-time use)
    delete_token(user_id)

    return jsonify({"status": "verified"})


# 🔎 Check verification (used by bot)
@app.route("/check")
def check():
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"verified": False})

    return jsonify({"verified": is_verified(user_id)})


# 🚀 Run Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)