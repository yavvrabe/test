from flask import Flask, request, jsonify
from flask_cors import CORS
from mega import Mega
import os
from dotenv import load_dotenv
import threading
import time

# Load .env
load_dotenv()

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

mega = Mega()

# login to Mega once
try:
    m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
    print("✅ Mega login success")
except Exception as e:
    print("❌ Mega login failed:", e)
    m = None

app = Flask(__name__)
CORS(app)

# Cache allowed IDs
allowed_ids_cache = []

def load_ids_from_mega():
    """Download register.slfx from Mega and update cache."""
    global allowed_ids_cache
    if not m:
        print("❌ Mega not connected")
        allowed_ids_cache = []
        return

    try:
        files = m.get_files()
        target_key = None

        for key, meta in files.items():
            if isinstance(meta, dict):
                name = meta.get('a', {}).get('n')
                if name == 'register.slfx':
                    target_key = key
                    break

        if not target_key:
            print("❌ register.slfx not found")
            allowed_ids_cache = []
            return

        print("✅ Found file:", target_key)

        # Download temp
        m.download(target_key, 'register.slfx.tmp')

        # Read IDs
        with open('register.slfx.tmp', 'r') as f:
            allowed_ids_cache = [line.strip() for line in f if line.strip()]

        os.remove('register.slfx.tmp')
        print("✅ IDS LOADED:", allowed_ids_cache)

    except Exception as e:
        print("❌ FINAL ERROR:", e)
        allowed_ids_cache = []

# Load IDs on server start
load_ids_from_mega()

# Optional: refresh cache every 5 minutes
def refresh_cache_loop():
    while True:
        time.sleep(300)  # 5 minutes
        print("🔄 Refreshing allowed IDs cache from Mega...")
        load_ids_from_mega()

threading.Thread(target=refresh_cache_loop, daemon=True).start()

# 🔐 Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        user_id = data.get("id", "").strip()
        print("📩 Login attempt:", user_id)
        print("ALLOWED IDS:", allowed_ids_cache)

        if user_id in allowed_ids_cache:
            return jsonify({"success": True})

        return jsonify({"success": False, "msg": "Invalid ID"}), 401

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"success": False, "msg": "Server error"}), 500

@app.route('/')
def home():
    return "Yave server is running 🔥"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
