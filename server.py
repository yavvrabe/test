import asyncio
import websockets
import json
import os
from mega import Mega
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("MEGA_EMAIL")
PASSWORD = os.getenv("MEGA_PASSWORD")

mega = Mega()
m = mega.login(EMAIL, PASSWORD)

# fake ID check (you will replace with MEGA file later)
VALID_IDS = ["YAVE123"]

def get_all_files():
    return m.get_files()

def get_users():
    files = get_all_files()
    users = []

    for k, v in files.items():
        if v['a'].get('n') == "Data":
            parent = k
            for ck, cv in files.items():
                if cv['p'] == parent:
                    users.append(cv['a']['n'])
    return users

async def handler(ws):
    async for msg in ws:
        data = json.loads(msg)

        if data["action"] == "auth":
            if data["id"] in VALID_IDS:
                await ws.send(json.dumps({"type": "auth", "ok": True}))
            else:
                await ws.send(json.dumps({"type": "auth", "ok": False}))

        elif data["action"] == "users":
            await ws.send(json.dumps({
                "type": "users",
                "list": get_users()
            }))

        elif data["action"] == "files":
            files = get_all_files()
            result = []

            for k, v in files.items():
                name = v['a'].get('n')
                if name:
                    result.append(name)

            await ws.send(json.dumps({
                "type": "files",
                "list": result
            }))

start = websockets.serve(handler, "0.0.0.0", 3000)
asyncio.get_event_loop().run_until_complete(start)
asyncio.get_event_loop().run_forever()