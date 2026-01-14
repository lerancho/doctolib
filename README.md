# Hello Termux (Python CLI)

Petit projet Python "Hello World" pour valider l'exécution sur Termux.

## Prérequis (Termux)
- Installer Python et Git :
```sh
pkg update
pkg install python git
```

## Utilisation rapide (sans installation)
Cloner puis exécuter l'un des deux modes ci-dessous :
```sh
# 1) Script direct
python hello.py

# 2) Module package
python -m hellotermux
```

## Installation en CLI (optionnel)
Pour installer une commande système `hello-termux` :
```sh
git clone https://github.com/USERNAME/hello-termux.git
cd hello-termux
pip install --upgrade pip
pip install .
hello-termux
```

## Développement local
- Python 3.8+
- Aucun paquet externe requis

### Exécuter
```sh
python -m hellotermux
```

### Désinstallation (si installé)
```sh
pip uninstall hello-termux
```

## Notes
- Les fins de lignes sont en LF pour compatibilité Termux.
- Le package est à la racine (pas de layout `src/`) pour permettre `python -m hellotermux` sans installation.
