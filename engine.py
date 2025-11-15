#!/usr/bin/env python3
import os, json, requests, asyncio, websockets

SERVER = "https://gophub.onrender.com"
STORAGE_DIR = os.path.expanduser("~/.goputn")
os.makedirs(STORAGE_DIR, exist_ok=True)

def save_log(env, cmd, output):
    log_file = os.path.join(STORAGE_DIR, "session.log")
    with open(log_file, "a") as f:
        f.write(f"[{env}] $ {cmd}\n{output}\n\n")

def run_http(env, cmd):
    url = f"{SERVER}/terminal"
    payload = {"env": env, "command": cmd}
    r = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    result = r.json()
    output = result.get("output", "")
    save_log(env, cmd, output)
    return output

async def run_ws(env):
    async with websockets.connect(f"{SERVER.replace('https','wss')}/terminal/ws") as ws:
        print("Session interactive ouverte 🚀 (WebSocket)")
        while True:
            cmd = input("gopuTN(ws) > ").strip()
            if cmd in ("exit", "quit"):
                print("Fermeture session WebSocket.")
                break
            await ws.send(cmd)
            output = await ws.recv()
            print(output)
            save_log(env, cmd, output)

def main():
    env = "ubuntu:22.04"
    print("Moteur gopuTN lancé 🚀")
    while True:
        cmd = input("gopuTN > ").strip()
        if cmd in ("exit", "quit"):
            print("Fermeture moteur gopuTN.")
            break
        elif cmd == "ws":
            asyncio.run(run_ws(env))
        else:
            output = run_http(env, cmd)
            print(output)

if __name__ == "__main__":
    main()

