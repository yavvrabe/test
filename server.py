from flask import Flask, request, jsonify
from flask_cors import CORS
from megapy import Mega
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

app = Flask(__name__)
CORS(app)

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")
MEGA_FILE = "Fatch/register.slfx"

def get_allowed_ids():
    try:
        mega = Mega()
        m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)
        # download the register.slfx content as text
        file = m.find(MEGA_FILE)
        if not file:
            print("File not found on Mega:", MEGA_FILE)
            return []
        content = m.download(file, dest=None).read().decode()
        return [line.strip() for line in content.splitlines() if line.strip()]
    except Exception as e:
        print("Error fetching register.slfx from Mega:", e)
        return []

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user_id = data.get("id", "").strip()

    allowed_ids = get_allowed_ids()

    if user_id in allowed_ids:
        return jsonify({"success": True, "message": "Access Granted"})
    else:
        return jsonify({"success": False, "message": "Invalid ID"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
