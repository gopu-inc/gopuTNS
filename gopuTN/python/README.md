# Environnement Python pour gopuTN

Ce package fournit un environnement Python prêt à l’emploi pour gopHub.

## Instructions

- **Base** : `REC python:latest`
- **Installations** :
  - Python3
  - pip
  - setuptools
  - wheel
- **Test** : `python3 --version`

## Utilisation

Dans un fichier `.gopuTN` :

```text
REC gotn:python:latest
LOC /app
BY app.py /app/
DO pip install fastapi uvicorn
NET 8000
GO ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
