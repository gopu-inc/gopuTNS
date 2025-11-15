#!/usr/bin/env python3
import os, json, time, asyncio, requests, websockets
from datetime import datetime

# ------------------------
# Dossier de sauvegarde
# ------------------------
def resolve_storage_dir():
    # Priorité: dossier local .goputn, sinon HOME/.goputn
    local_dir = os.path.join(os.getcwd(), ".goputn")
    if os.path.isdir(local_dir) or not os.path.isdir(os.path.expanduser("~/.goputn")):
        return local_dir
    return os.path.expanduser("~/.goputn")

STORAGE_DIR = os.environ.get("GOPUTN_DIR", resolve_storage_dir())
CONFIG_PATH = os.path.join(STORAGE_DIR, "config.json")
HISTORY_PATH = os.path.join(STORAGE_DIR, "history.log")

# ------------------------
# Config par défaut
# ------------------------
DEFAULT_CONFIG = {
    "server": "https://terminalgo.onrender.com",
    "ws_path": "/terminal/ws",
    "http_path": "/terminal",
    "history_limit": 500,   # nb lignes dans history.log avant rotation
    "print_mode": "json"    # json | output
}

def ensure_storage():
    os.makedirs(STORAGE_DIR, exist_ok=True)
    if not os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
    if not os.path.isfile(HISTORY_PATH):
        open(HISTORY_PATH, "a", encoding="utf-8").close()

def load_config():
    ensure_storage()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    # merge avec defaults si nouveaux champs
    for k, v in DEFAULT_CONFIG.items():
        cfg.setdefault(k, v)
    return cfg

def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def append_history(entry: dict):
    ensure_storage()
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    line = json.dumps(entry, ensure_ascii=False)
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    # rotation simple si trop long
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
        cfg = load_config()
        if len(lines) > cfg.get("history_limit", 500):
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                f.writelines(lines[-cfg["history_limit"]:])
    except Exception:
        pass

# ------------------------
# HTTP /terminal
# ------------------------
def run_http(cmd: str, cfg: dict):
    url = cfg["server"].rstrip("/") + cfg["http_path"]
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(cmd))
        status = r.status_code
        try:
            result = r.json()
        except Exception:
            result = {"raw": r.text}
        append_history({"mode": "http", "command": cmd, "status": status, "response": result})
        if status != 200:
            return f"Erreur HTTP {status}: {r.text}"
        if cfg.get("print_mode") == "output" and isinstance(result, dict) and "output" in result:
            return result.get("output", "")
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        append_history({"mode": "http", "command": cmd, "error": str(e)})
        return f"Erreur HTTP: {str(e)}"

# ------------------------
# WebSocket /terminal/ws
# ------------------------
async def run_ws(cfg: dict):
    ws_url = cfg["server"].replace("https://", "wss://").replace("http://", "ws://").rstrip("/") + cfg["ws_path"]
    try:
        async with websockets.connect(ws_url) as ws:
            welcome = await ws.recv()
            print(welcome)
            append_history({"mode": "ws", "event": "connected", "url": ws_url, "welcome": welcome})
            while True:
                cmd = input("gopuTN(ws) > ").strip()
                if cmd in ("exit", "quit"):
                    print("Fermeture session interactive.")
                    append_history({"mode": "ws", "event": "exit"})
                    break
                await ws.send(cmd)
                try:
                    output = await ws.recv()
                    print(output)
                    append_history({"mode": "ws", "command": cmd, "response": output})
                except Exception as e:
                    print(f"Erreur WebSocket: {str(e)}")
                    append_history({"mode": "ws", "command": cmd, "error": str(e)})
                    break
    except Exception as e:
        print(f"Impossible de se connecter au WebSocket: {str(e)}")
        append_history({"mode": "ws", "event": "connect_error", "error": str(e)})

# ------------------------
# Commandes utilitaires
# ------------------------
def handle_meta(cmd: str, cfg: dict):
    # config set server https://...
    parts = cmd.split()
    if parts[:2] == ["config", "get"]:
        # ex: config get server
        key = parts[2] if len(parts) > 2 else None
        if key:
            print(json.dumps({key: cfg.get(key)}, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(cfg, indent=2, ensure_ascii=False))
        return True
    if parts[:2] == ["config", "set"] and len(parts) >= 4:
        # ex: config set server https://...
        key = parts[2]
        value = " ".join(parts[3:])
        cfg[key] = value
        save_config(cfg)
        print(f"Config mise à jour: {key} = {value}")
        append_history({"mode": "meta", "action": "config_set", "key": key, "value": value})
        return True
    if cmd == "history show":
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()[-50:]  # montrer les 50 dernières lignes
            print("— Dernières entrées history.log —")
            for ln in lines:
                print(ln.rstrip())
        except Exception as e:
            print(f"Erreur lecture history: {str(e)}")
        return True
    if cmd == "history clear":
        try:
            open(HISTORY_PATH, "w", encoding="utf-8").close()
            print("Historique vidé.")
            append_history({"mode": "meta", "action": "history_clear"})
        except Exception as e:
            print(f"Erreur clear history: {str(e)}")
        return True
    if parts[:2] == ["print", "mode"] and len(parts) == 3:
        # ex: print mode output | json
        val = parts[2]
        if val in ("output", "json"):
            cfg["print_mode"] = val
            save_config(cfg)
            print(f"Print mode = {val}")
            append_history({"mode": "meta", "action": "print_mode", "value": val})
            return True
        else:
            print("Valeurs autorisées: output | json")
            return True
    return False

# ------------------------
# Boucle principale
# ------------------------
def main():
    ensure_storage()
    cfg = load_config()
    print(f"Moteur gopuTN lancé 🚀  (storage: {STORAGE_DIR})")
    print("Tips: 'ws' pour session interactive, 'config get', 'config set', 'history show', 'print mode output|json'")
    while True:
        cmd = input("gopuTN > ").strip()
        if not cmd:
            continue
        if cmd in ("exit", "quit"):
            print("Fermeture moteur gopuTN.")
            append_history({"mode": "meta", "action": "exit"})
            break
        if handle_meta(cmd, cfg):
            continue
        if cmd == "ws":
            print("Session interactive ouverte 🚀 (WebSocket)")
            asyncio.run(run_ws(cfg))
            continue
        # Commande standard via HTTP
        out = run_http(cmd, cfg)
        print(out)

if __name__ == "__main__":
    main()
