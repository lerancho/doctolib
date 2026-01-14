# Hello Termux (Python CLI)

Petit projet Python pour valider l'exécution sur Termux et vérifier des disponibilités de rendez-vous sur une période.

## Prérequis (Termux)
- Installer Python et Git :
```sh
pkg update
pkg install python git
```

## Utilisation rapide (sans installation)
Configurer puis exécuter :
```sh
# 1) Éditer la configuration
# Ouvrir config.json et renseigner master_patient_signed_id si requis

# 2) Lancer un scan (CLI minimale)
python scan.py -rdv m6 -prat criton
```

## Installation en CLI (optionnel)
Pour installer une commande système `rdv-scan` :
```sh
git clone https://github.com/lerancho/doctolib.git
cd doctolib
pip install --upgrade pip
pip install .
rdv-scan -rdv m6 -prat criton
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
python scan.py -rdv m6 -prat criton
```

### Désinstallation (si installé)
```sh
pip uninstall hello-termux
```

## Notes
- Les fins de lignes sont en LF pour compatibilité Termux.
 - Le package expose une commande `rdv-scan` après installation, sinon utilisez `python scan.py`.
 - Provider distant: utilise une URL compatible Doctolib. Respectez les CGU/TOS du service.
 - Notification: si `termux-notification` est disponible, une notification Android est envoyée.
 - Déduplication: les créneaux déjà notifiés sont stockés dans `data/notified.txt` et ne seront plus notifiés.
 - Toute configuration (URL, token, alias, months, limit) vit dans `config.json`.

### Aliases fournis
- RDV:
	- `m6` → `visit_motive_ids=6425744`, `agenda_ids=942956`
	- `p6` → `visit_motive_ids=6425745`, `agenda_ids=942956`
- Praticien:
	- `criton` → `practice_ids=6425745`
