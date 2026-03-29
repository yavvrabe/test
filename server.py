import asyncio
import websockets
import json
import os
from mega import Mega
from dotenv import load_dotenv

# Load env variables FIRST
load_dotenv()
EMAIL = os.getenv("MEGA_EMAIL")
PASSWORD = os.getenv("MEGA_PASSWORD")

# MEGA login
mega = Mega()
m = mega.login(EMAIL, PASSWORD)

# fake ID check (replace with your logic)
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

# Unified websocket handler
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
            result = [v['a'].get('n') for k,v in files.items() if v['a'].get('n')]
            await ws.send(json.dumps({
                "type": "files",
                "list": result
            }))

async def main():
    # Use Railway PORT if provided
    PORT = int(os.environ.get("PORT", 3000))
    async with websockets.serve(handler, "0.0.0.0", PORT):
        print(f"WebSocket server running on port {PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
