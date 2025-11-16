import os
import re
import sys
from setuptools import setup, find_packages
import urllib.request
import json

PACKAGE_NAME = "goputn"
VERSION = "0.3.0"

# 1. Vérifier la structure
if not os.path.isdir(PACKAGE_NAME) or not os.path.isfile(os.path.join(PACKAGE_NAME, "__init__.py")):
    print(f"⚠️ Structure invalide : dossier {PACKAGE_NAME}/ ou __init__.py manquant")
    sys.exit(1)

# 2. Vérifier la version sur PyPI
try:
    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
        versions = list(data.get("releases", {}).keys())
        if VERSION in versions:
            # incrémenter automatiquement
            major, minor, patch = map(int, VERSION.split("."))
            VERSION = f"{major}.{minor}.{patch+1}"
            print(f"⚡ Version {VERSION} choisie car {VERSION} existait déjà sur PyPI")
except Exception as e:
    print(f"ℹ️ Impossible de vérifier PyPI : {e}")

# 3. Setup avec entry points
setup(
    name=PACKAGE_NAME,
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "goputn=engine:main",
            "gopuTN=engine:main",
            "gotn=gopuTN.gotn.cli:main",
        ],
    },
    install_requires=[],
    description="Branded runtime for goputn/gopuTN/gotn",
    author="Mauricio-100",
    author_email="ceoseshell@gmail.com",
    url="https://github.com/gopu-inc/gopuTNS",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
