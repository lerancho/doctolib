# Hello Termux (Python CLI)

Petit projet Python pour valider l'exécution sur Termux et vérifier des disponibilités de rendez-vous sur une période.

## Prérequis (Termux)
- Installer Python et Git :
```sh
pkg update
pkg install python git
```

## Utilisation rapide (sans installation)
Cloner puis exécuter l'un des modes ci-dessous :
```sh
# 1) Script direct
python hello.py

# 2) Module package
python -m hellotermux

# 3) Vérifier des disponibilités à partir d'un JSON local
python -m hellotermux check --file ./data/slots.sample.json --months 3 --from 2026-01-14
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

### Format JSON attendu
Fichier simple avec la clé `slots` contenant des objets `{start, end}` au format ISO:
```json
{
	"slots": [
		{"start": "2026-02-12T09:00:00", "end": "2026-02-12T09:15:00"}
	]
}
```

### Exécuter
```sh
python -m hellotermux
python -m hellotermux check --file ./data/slots.sample.json --months 2
```

### Désinstallation (si installé)
```sh
pip uninstall hello-termux
```

## Notes
- Les fins de lignes sont en LF pour compatibilité Termux.
- Le package est à la racine (pas de layout `src/`) pour permettre `python -m hellotermux` sans installation.
 - Le provider actuel lit un fichier local JSON pour démonstration. L'intégration à une API distante devra respecter ses CGU/TOS.
