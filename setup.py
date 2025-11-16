from setuptools import setup, find_packages
import urllib.request, json

PACKAGE_NAME = "goputn"
VERSION = "0.3.1"

# Vérifier la version sur PyPI et incrémenter si nécessaire
try:
    url = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.load(resp)
        versions = list(data.get("releases", {}).keys())
        if VERSION in versions:
            major, minor, patch = map(int, VERSION.split("."))
            VERSION = f"{major}.{minor}.{patch+1}"
            print(f"⚡ Version {VERSION} choisie car {VERSION} existait déjà sur PyPI")
except Exception as e:
    print(f"ℹ️ Impossible de vérifier PyPI : {e}")

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "gopuTN=engine:main",
            "goputn=engine:main",
            "gotn=gopuTN.gotn.cli:main",
        ],
    },
    description="Branded runtime with gopuTN, goputn, gotn commands",
    author="Ceose",
    url="https://github.com/gopu-inc/gopuTNS",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
