from flask import Flask, request, jsonify
from flask_cors import CORS
from mega import Mega
import os
from dotenv import load_dotenv

# load env
load_dotenv()

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

mega = Mega()

try:
    m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
    print("✅ Mega login success")
except Exception as e:
    print("❌ Mega login failed:", e)
    m = None

app = Flask(__name__)
CORS(app)

# 🔑 Get IDs safely
def get_allowed_ids():
    try:
        if not m:
            print("❌ Mega not connected")
            return []

        files = m.find('register.slfx')
        if not files:
            print("❌ register.slfx not found")
            return []

        file = files[0]
        m.download(file, 'register.slfx.tmp')

        with open('register.slfx.tmp', 'r') as f:
            ids = [line.strip() for line in f if line.strip()]

        os.remove('register.slfx.tmp')  # clean up

        return ids

    except Exception as e:
        print("❌ Error reading Mega file:", e)
        return []

# 🔐 Login route
@app.route('/login', methods=['POST'])
@app.route('/')
def home():
    return "Yave server is running 🔥"
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "msg": "No data"}), 400

        user_id = data.get("id", "").strip()

        allowed = get_allowed_ids()

        if user_id in allowed:
            return jsonify({"success": True})

        return jsonify({"success": False, "msg": "Invalid ID"}), 401

    except Exception as e:
        print("❌ Login error:", e)
        return jsonify({"success": False, "msg": "Server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
