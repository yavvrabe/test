from flask import Flask, request, jsonify
from flask_cors import CORS
from mega import Mega
import os
from dotenv import load_dotenv
import threading
import time

# load .env
load_dotenv()
MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

# Mega login and cache
mega = Mega()
m = None
allowed_ids = []

def refresh_allowed_ids():
    global m, allowed_ids
    while True:
        try:
            if not m:
                m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
                print("✅ Mega login success")

            files = m.get_files()
            target_key = None

            for key, meta in files.items():
                # Only proceed if meta is a dict and has 'a'
                if isinstance(meta, dict) and 'a' in meta and isinstance(meta['a'], dict):
                    name = meta['a'].get('n')
                    if name == 'register.slfx':
                        target_key = key
                        break

            if target_key:
                m.download(target_key, 'register.slfx.tmp')
                with open('register.slfx.tmp', 'r') as f:
                    allowed_ids = [line.strip() for line in f if line.strip()]
                os.remove('register.slfx.tmp')
                print(f"✅ Allowed IDs refreshed: {allowed_ids}")
            else:
                print("❌ register.slfx not found")

        except Exception as e:
            print("❌ Error refreshing Mega IDs:", e)

        time.sleep(600)  # refresh every 10 minutes

# start background thread to refresh IDs
threading.Thread(target=refresh_allowed_ids, daemon=True).start()

# Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Yave server is running 🔥"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_id = data.get("id", "").strip()
        if user_id in allowed_ids:
            return jsonify({"success": True})
        return jsonify({"success": False, "msg": "Invalid ID"}), 401
    except Exception as e:
        print("❌ Login error:", e)
        return jsonify({"success": False, "msg": "Server error"}), 500
