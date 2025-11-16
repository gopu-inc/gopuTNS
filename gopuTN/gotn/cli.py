#!/usr/bin/env python3
import argparse
import os
import sys
import json
import requests
import websocket

API = "https://gophub.onrender.com"
CONFIG = os.path.expanduser("~/.gotnrc")

# ---------------------------
# Utilitaires
# ---------------------------

def save_token(token):
    os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
    with open(CONFIG, "w") as f:
        json.dump({"token": token}, f)
    print("[gopuTN] ✅ Token enregistré dans .gotnrc")

def load_token():
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            return json.load(f).get("token")
    return None

def auth_header():
    token = load_token()
    if not token:
        print("[gopuTN] ❌ Aucun token trouvé, fais 'gotn login' d'abord")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}

def safe_print_response(res):
    print(f"[HTTP {res.status_code}]")
    try:
        print(json.dumps(res.json(), indent=2))
    except Exception:
        print("[gopuTN] ℹ️ Réponse brute du serveur:", res.text)

# ---------------------------
# Commandes CLI
# ---------------------------

def cmd_login(args):
    print("[gopuTN] ℹ️ Connexion à gopHub...")
    res = requests.post(API+"/login", json={"email": args.email, "password": args.password})
    safe_print_response(res)
    if res.ok and "token" in res.json():
        save_token(res.json()["token"])

def cmd_register(args):
    print("[gopuTN] ℹ️ Création de compte...")
    res = requests.post(API+"/register", json={"email": args.email, "password": args.password})
    safe_print_response(res)

def cmd_list(args):
    res = requests.get(API+"/list")
    safe_print_response(res)

def cmd_search(args):
    res = requests.get(f"{API}/search?q={args.query}")
    safe_print_response(res)

def cmd_readme(args):
    res = requests.get(f"{API}/readme/{args.name}/{args.version}")
    if res.ok:
        print(res.text)
    else:
        safe_print_response(res)

def cmd_stats(args):
    res = requests.get(f"{API}/stats/{args.name}/{args.version}")
    safe_print_response(res)

def cmd_assoc(args):
    res = requests.get(f"{API}/search?q=@{args.scope}/")
    safe_print_response(res)

def cmd_send(args):
    token = load_token()
    if not token:
        print("[gopuTN] ❌ Aucun token trouvé, fais 'gotn login' d'abord")
        return

    if os.path.exists("gotn.json"):
        with open("gotn.json") as f:
            config = json.load(f)
        pkg_name = config["name"]
        version = config["version"]
        files = config["files"]
        tags = args.tags or []
        print(f"[gopuTN] ℹ️ Publication du package '{pkg_name}:{version}' avec {len(files)} fichiers...")
        file_objs = [("files", open(f, "rb")) for f in files if os.path.exists(f)]
        res = requests.post(API+"/push",
            headers={"Authorization": f"Bearer {token}"},
            data={"name": pkg_name, "version": version, "tags": json.dumps(tags)},
            files=file_objs)
        safe_print_response(res)
    else:
        print("[gopuTN] ❌ gotn.json introuvable, fais 'gotn init' d'abord")

def cmd_init(args):
    config = {
        "name": args.name,
        "version": args.version,
        "files": args.files,
        "tags": args.tags
    }
    with open("gotn.json", "w") as f:
        json.dump(config, f, indent=2)
    print("[gopuTN] ✅ Fichier gotn.json créé")

def cmd_exec(args):
    res = requests.post(API+"/terminal",
                        headers=auth_header(),
                        json={"env": args.env, "command": args.command})
    safe_print_response(res)

def cmd_env_create(args):
    res = requests.post(API+"/env/create",
                        headers=auth_header(),
                        data={"name": args.name,
                              "version": args.version,
                              "description": args.description,
                              "tags": json.dumps(args.tags)})
    safe_print_response(res)

def cmd_update(args):
    res = requests.post(f"{API}/update/{args.name}/{args.version}",
                        headers=auth_header(),
                        json={"description": args.description, "tags": args.tags})
    safe_print_response(res)

def cmd_delete(args):
    res = requests.delete(f"{API}/delete/{args.name}/{args.version}",
                          headers=auth_header())
    safe_print_response(res)

def cmd_pull(args):
    res = requests.get(f"{API}/pull/{args.name}/{args.version}/{args.filename}",
                       headers=auth_header())
    if res.ok:
        with open(args.filename, "wb") as f:
            f.write(res.content)
        print(f"[gopuTN] ✅ Fichier téléchargé: {args.filename}")
    else:
        safe_print_response(res)

def cmd_shell(args):
    ws_url = API.replace("http", "ws") + "/terminal/ws"
    ws = websocket.WebSocket()
    ws.connect(ws_url)
    print(ws.recv())
    try:
        while True:
            cmd = input(f"{args.env}:{args.version}$ ")
            ws.send(cmd)
            print(ws.recv())
    except KeyboardInterrupt:
        ws.close()

# ---------------------------
# Transpileur .gopuTN
# ---------------------------

def cmd_const(args):
    infile = args.file
    if not os.path.exists(infile):
        print("[gopuTN] ❌ Fichier introuvable:", infile)
        return

    manifest = {"commands": []}
    with open(infile) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(maxsplit=1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else ""

            # Normaliser CREATE
            if cmd in ["CREATE", "CREAT"]:
                cmd = "CREATE"

            # Normaliser GO avec préfixe g:
            if cmd == "GO" and arg.startswith("["):
                try:
                    arr = json.loads(arg)
                    if arr and isinstance(arr[0], str) and not arr[0].startswith("g:"):
                        arr[0] = "g:" + arr[0]
                    arg = json.dumps(arr)
                except Exception:
                    pass

            manifest["commands"].append({"cmd": cmd, "arg": arg})

    out = infile.replace(".gopuTN", ".json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[gopuTN] ✅ Manifest généré: {out}")

def cmd_let(args):
    infile = args.file
    manifest = infile.replace(".gopuTN", ".json")
    if not os.path.exists(manifest):
        print("[gopuTN] ❌ Manifest introuvable, fais 'gotn const' d'abord")
        return

    with open(manifest) as f:
        data = json.load(f)

    print("[gopuTN] ℹ️ Exécution du manifest...")
    for entry in data["commands"]:
        cmd = entry["cmd"]
        arg = entry["arg"]
        print(f" → {cmd} {arg}")
        if cmd == "DO":
            os.system(arg)
        elif cmd == "NET":
            print(f"[gopuTN] 🌐 Port exposé: {arg}")
        elif cmd == "REC":
            print(f"[gopuTN] 📦 Environnement requis: {arg}")
        elif cmd == "LOC":
            print(f"[gopuTN] 📂 Workdir: {arg}")
        elif cmd == "BY":
            print(f"[gopuTN] 📥 Copie: {arg}")
        elif cmd == "GO":
            os.system(" ".join(json.loads(arg)))
        elif cmd == "CREATE":
            print(f"[gopuTN] 🏗️ Création d'environnement: {arg}")

# ---------------------------
# Main
# ---------------------------

def main():
    parser = argparse.ArgumentParser(prog="gotn", description="gopHub CLI 🚀 — gestion des packages, environnements et manifests .gopuTN")
    sub = parser.add_subparsers(dest="command")

    # login / register
    p_login = sub.add_parser("login", help="Connexion à gopHub"); p_login.add_argument("email"); p_login.add_argument("password"); p_login.set_defaults(func=cmd_login)
    p_register = sub.add_parser
      # list / search / readme / stats / assoc
    p_list = sub.add_parser("list", help="Lister tous les packages disponibles")
    p_list.set_defaults(func=cmd_list)

    p_search = sub.add_parser("search", help="Rechercher un package par mot-clé ou tag")
    p_search.add_argument("query")
    p_search.set_defaults(func=cmd_search)

    p_readme = sub.add_parser("readme", help="Afficher le README d’un package")
    p_readme.add_argument("name")
    p_readme.add_argument("version")
    p_readme.set_defaults(func=cmd_readme)

    p_stats = sub.add_parser("stats", help="Afficher les statistiques d’un package")
    p_stats.add_argument("name")
    p_stats.add_argument("version")
    p_stats.set_defaults(func=cmd_stats)

    p_assoc = sub.add_parser("assoc", help="Lister les packages d’une association (@scope/*)")
    p_assoc.add_argument("scope")
    p_assoc.set_defaults(func=cmd_assoc)

    # send / init
    p_send = sub.add_parser("send", help="Publier un package défini dans gotn.json")
    p_send.add_argument("--tags", nargs="+", default=[], help="Tags du package")
    p_send.set_defaults(func=cmd_send)

    p_init = sub.add_parser("init", help="Créer un fichier gotn.json pour configurer un package")
    p_init.add_argument("name")
    p_init.add_argument("version")
    p_init.add_argument("files", nargs="+")
    p_init.add_argument("--tags", nargs="+", default=[], help="Tags du package")
    p_init.set_defaults(func=cmd_init)

    # env / exec / shell
    p_env = sub.add_parser("env", help="Créer un nouvel environnement sur gopHub")
    p_env.add_argument("name")
    p_env.add_argument("version")
    p_env.add_argument("--description", default="", help="Description de l’environnement")
    p_env.add_argument("--tags", nargs="+", default=[], help="Tags de l’environnement")
    p_env.set_defaults(func=cmd_env_create)

    p_exec = sub.add_parser("exec", help="Exécuter une commande dans un environnement")
    p_exec.add_argument("env")
    p_exec.add_argument("command")
    p_exec.set_defaults(func=cmd_exec)

    p_shell = sub.add_parser("shell", help="Ouvrir un shell interactif via WebSocket")
    p_shell.add_argument("env")
    p_shell.add_argument("version")
    p_shell.set_defaults(func=cmd_shell)

    # update / delete / pull
    p_update = sub.add_parser("update", help="Mettre à jour un package existant")
    p_update.add_argument("name")
    p_update.add_argument("version")
    p_update.add_argument("--description", default="", help="Nouvelle description")
    p_update.add_argument("--tags", nargs="+", default=[], help="Nouveaux tags")
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Supprimer un package")
    p_delete.add_argument("name")
    p_delete.add_argument("version")
    p_delete.set_defaults(func=cmd_delete)

    p_pull = sub.add_parser("pull", help="Télécharger un fichier depuis un package")
    p_pull.add_argument("name")
    p_pull.add_argument("version")
    p_pull.add_argument("filename")
    p_pull.set_defaults(func=cmd_pull)

    # const / let
    p_const = sub.add_parser("const", help="Transpiler un fichier .gopuTN en manifest JSON")
    p_const.add_argument("file")
    p_const.set_defaults(func=cmd_const)

    p_let = sub.add_parser("let", help="Exécuter un manifest JSON généré par const")
    p_let.add_argument("file")
    p_let.set_defaults(func=cmd_let)

    # Parse args et exécution
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
