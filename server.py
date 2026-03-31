from flask import Flask, request, jsonify
from flask_cors import CORS
from mega import Mega
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

MEGA_EMAIL = os.getenv("MEGA_EMAIL")
MEGA_PASSWORD = os.getenv("MEGA_PASSWORD")

mega = Mega()
m = mega.login(MEGA_EMAIL, MEGA_PASSWORD)

app = Flask(__name__)
CORS(app)

# Read allowed IDs from your private file
def get_allowed_ids():
    file = m.find('register.slfx')[0]  # make sure the file exists
    download = m.download(file, dest='register.slfx.tmp')
    with open('register.slfx.tmp', 'r') as f:
        ids = [line.strip() for line in f if line.strip()]
    os.remove('register.slfx.tmp')
    return ids

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get("id")
    allowed = get_allowed_ids()
    if user_id in allowed:
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "Invalid ID"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
