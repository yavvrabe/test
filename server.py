from flask import Flask, request, jsonify
from flask_cors import CORS
from mega import Mega
import os
from dotenv import load_dotenv

# Load .env
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

# 🔑 Safely get allowed IDs from Mega
def get_allowed_ids():
    try:
        if not m:
            print("❌ Mega not connected")
            return []

        files = m.get_files()
        print("FILES TYPE:", type(files))
        print("FILES SAMPLE:", list(files)[:3])

        target_key = None

        # Loop safely through files
        for key, meta in files.items():
            if not isinstance(meta, dict):
                continue

            attrs = meta.get('a')
            if not isinstance(attrs, dict):
                continue

            name = attrs.get('n')
            if name == 'register.slfx':
                target_key = key
                break

        if not target_key:
            print("❌ register.slfx not found")
            return []

        print("✅ Found file:", target_key)

        # Download safely using the file node
        m.download(files[target_key], 'register.slfx.tmp')

        # Read IDs
        with open('register.slfx.tmp', 'r') as f:
            ids = [line.strip() for line in f if line.strip()]

        os.remove('register.slfx.tmp')  # cleanup
        print("✅ IDS LOADED:", ids)

        return ids

    except Exception as e:
        print("❌ FINAL ERROR:", e)
        return []

# 🔐 Login route
@app.route('/login', methods=['POST'])
def login():
    print("📩 Login request received")
    try:
        data = request.get_json()
        print("DATA:", data)

        user_id = data.get("id", "").strip()
        print("USER ID:", user_id)

        allowed = get_allowed_ids()
        print("ALLOWED IDS:", allowed)

        if user_id in allowed:
            return jsonify({"success": True})

        return jsonify({"success": False, "msg": "Invalid ID"}), 401

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"success": False, "msg": "Server error"}), 500

# 🏠 Home route
@app.route('/')
def home():
    return "Yave server is running 🔥"

if __name__ == '__main__':
    # Debug off for production on Railway
    #app.run(host='0.0.0.0', port=8080)
    pass
