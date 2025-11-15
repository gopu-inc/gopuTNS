<img width="1024" height="1024" alt="IMG_6946" src="https://github.com/user-attachments/assets/bfe012ec-627c-4195-8a49-ec45826e746d" />


# gopuTN / gotn ⚡🐨🔥

[![Build Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ceose/gopuTNS)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**`gopuTN` est un moteur en ligne de commande (CLI) conçu pour interagir avec un backend FastAPI, offrant une expérience immersive et puissante. Son alias, `gotn`, propose un accès rapide et stylisé, incarnant une philosophie agentique basée sur la modularité, l'introspection et une interaction fluide.**

---

## 🚀 Introduction

Ce projet fournit un ensemble d'outils pour exécuter des commandes à distance, gérer des paquets et interagir avec des environnements sécurisés via une interface en ligne de commande intuitive. Il est conçu pour les développeurs qui recherchent une solution à la fois robuste et élégante pour leurs opérations quotidiennes.

---

## ✨ Fonctionnalités

*   **🔧 Exécution de commandes à distance** : Interagissez avec un serveur via des requêtes HTTP ou des sessions WebSocket persistantes.
*   **🗂️ Persistance locale** : La configuration et l'historique des commandes sont sauvegardés dans un répertoire local `.goputn` pour une utilisation cohérente.
*   **🪄 Double interface CLI** : Utilisez `goputn` pour le moteur principal et `gotn` pour un accès rapide et des fonctionnalités étendues de gestion de paquets.
*   **⚙️ Configuration dynamique** : Modifiez facilement les paramètres, comme l'URL du serveur, directement depuis la ligne de commande.
*   **🎨 Modes d'affichage flexibles** : Choisissez entre une sortie brute (`output`) ou un format JSON détaillé (`json`) pour s'adapter à vos besoins de scripting.
*   **📦 Gestion complète des paquets** : Authentifiez-vous, publiez, recherchez, mettez à jour et supprimez des paquets sur un hub central (`gopHub`).

---

## 📂 Structure du projet

```
gopuTNS/
├── engine.py              # Moteur principal du CLI (goputn)
├── setup.py               # Script de packaging et d'installation
├── gopuTN/
│   ├── gotn/
│   │   ├── __init__.py
│   │   └── cli.py         # CLI secondaire pour la gestion de paquets (gotn)
│   ├── app.py             # Serveur backend FastAPI
│   └── Dockerfile         # Configuration pour le déploiement en conteneur
└── README.md              # Ce fichier
```

---

## ⚙️ Installation

1.  **Cloner le dépôt**
    Clonez le projet sur votre machine locale pour commencer.
    ```bash
    git clone https://github.com/ceose/gopuTNS.git
    cd gopuTNS
    ```

2.  **Installer en mode éditable**
    Cette commande installe le projet et ses dépendances tout en vous permettant de modifier le code source et de voir les changements immédiatement.
    ```bash
    pip install -e .
    ```

3.  **Vérifier l'installation**
    Assurez-vous que les deux commandes sont accessibles depuis votre terminal.
    ```bash
    goputn --version
    gotn --help
    ```

---

## 🖥️ Utilisation de `goputn`

### Mode interactif

Lancez une session interactive pour exécuter des commandes en continu.

```bash
goputn
```

**Exemple :**
```
Moteur gopuTN lancé 🚀 (storage: ~/.goputn)
gopuTN > ls
{
  "command": "ls",
  "status": "ok",
  "output": "__pycache__\nrequirements.txt\nterminal_server.py\n"
}```

### Mode direct

Exécutez une seule commande et quittez.

```bash
goputn "echo hello world"
```

### Session WebSocket

Ouvrez une connexion WebSocket persistante pour une communication en temps réel avec le serveur.

```bash
goputn ws
```

---

## 🛠️ Commandes `goputn`

| Commande                       | Description                                                     |
| ------------------------------ | --------------------------------------------------------------- |
| `init`                         | Initialise le dossier `.goputn` dans le répertoire utilisateur. |
| `ws`                           | Ouvre une session interactive via WebSocket.                    |
| `config get`                   | Affiche la configuration actuelle.                              |
| `config set <clé> <valeur>`    | Modifie une valeur dans la configuration.                       |
| `history show`                 | Affiche les 50 dernières commandes de l'historique.             |
| `history clear`                | Efface tout l'historique des commandes.                         |
| `print mode <output\|json>`    | Change le mode d'affichage de la sortie.                        |

---

## 📦 Utilisation et commandes de `gotn`

L'alias `gotn` est votre portail vers `gopHub` pour la gestion des paquets et des environnements.

### 🔐 Authentification

| Commande                                           | Description                                                            |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| `gotn login --email <email> --password <password>` | Connectez-vous à `gopHub` et enregistrez votre jeton d'authentification. |
| `gotn register --email <email> --password <pass>`  | Créez un nouveau compte utilisateur sur `gopHub`.                      |

### 📤 Publication de paquets

| Commande                                                       | Description                                                               |
| -------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `gotn init --name <nom> --version <ver> --files <fichiers...>` | Crée un fichier de manifeste `gotn.json` pour définir votre paquet.       |
| `gotn send --tags <tags...>`                                   | Publie le paquet défini dans `gotn.json` sur `gopHub`.                    |

### 📦 Gestion des paquets

| Commande                        | Description                                                |
| ------------------------------- | ---------------------------------------------------------- |
| `gotn list`                     | Liste tous les paquets disponibles sur `gopHub`.           |
| `gotn search <requête>`         | Recherche un paquet par nom ou mot-clé.                    |
| `gotn readme <nom> <version>`   | Affiche le fichier README d'un paquet spécifique.          |
| `gotn stats <nom> <version>`    | Affiche les statistiques de téléchargement d'un paquet.    |
| `gotn pull <n> <v> <fichier>`   | Télécharge un fichier spécifique depuis une version d'un paquet. |
| `gotn assoc <scope>`            | Liste les paquets associés à un scope (ex: `@mon-scope/`). |

### ⚙️ Maintenance des paquets

| Commande                                                    | Description                                                  |
| ----------------------------------------------------------- | ------------------------------------------------------------ |
| `gotn update <n> <v> --description <desc> --tags <tags...>` | Met à jour la description et les tags d'un paquet publié.    |
| `gotn delete <nom> <version>`                               | Supprime une version spécifique d'un paquet de `gopHub`.     |

---

## 🌐 Architecture et Déploiement

Le **backend** est un serveur **FastAPI** qui expose deux points d'accès principaux :
*   `POST /terminal` : Pour exécuter une commande unique via `subprocess.run`.
*   `WS /terminal/ws` : Pour établir une session interactive persistante.

Ce serveur est déployé sur **Render** et est accessible publiquement à l'adresse :
[https://terminalgo.onrender.com](https://terminalgo.onrender.com)

---

## 🚀 Roadmap

*   [ ] **Environnements persistants** : Ajout de la commande `config env` pour gérer des variables d'environnement.
*   [ ] **Stylisation améliorée** : Intégration de `coloredlogs` pour des sorties plus lisibles et esthétiques.
*   [ ] **Packaging moderne** : Migration vers `pyproject.toml` pour une gestion des dépendances et une construction de paquets conformes aux standards actuels.
*   [ ] **Réinitialisation d'environnement** : Ajout d'une route `/terminal/reset` pour nettoyer l'état du serveur.
*   [ ] **Intégration `gopHub`** : Finalisation de l'intégration pour la publication et la gestion des paquets.

---

## 📜 Licence

Ce projet est distribué sous la **Licence MIT**. Consultez le fichier `LICENSE` pour plus de détails.

---

<p align="center">
  <em>Fait avec ❤️ par la communauté gopu.inc 🐨</em>
</p>
