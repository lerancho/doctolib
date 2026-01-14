from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from typing import Optional

from .config import load_config
from .providers.http_doctolib import fetch_availabilities
from .storage import load_notified, mark_notified, make_key, write_notified
from .notify import notify
FRENCH_WEEKDAYS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]

FRENCH_MONTHS = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]

def _format_slot_french(slot_iso: str) -> tuple[str, str]:
    """Return (day_text, time_text) from an ISO slot, e.g., ("Mardi 20 janvier", "14:30")."""
    try:
        dt = datetime.fromisoformat(slot_iso.replace("Z", "+00:00"))
    except Exception:
        # Fallback: return raw ISO
        return slot_iso, ""
    weekday = FRENCH_WEEKDAYS[dt.weekday()]
    day = dt.day
    month = FRENCH_MONTHS[dt.month - 1]
    time_txt = f"{dt:%H:%M}"
    day_txt = f"{weekday} {day} {month}"
    return day_txt, time_txt



def _advance_to_next_start(resp: dict, current_start: date) -> date:
    next_slot = resp.get("next_slot")
    if next_slot:
        try:
            dt = datetime.fromisoformat(next_slot.replace("Z", "+00:00"))
            return dt.date()
        except Exception:
            pass
    av = resp.get("availabilities") or []
    last_date = None
    for item in av:
        try:
            last_date = datetime.strptime(item.get("date"), "%Y-%m-%d").date()
        except Exception:
            continue
    return (last_date or current_start) + timedelta(days=1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scanner de disponibilités (config via fichier JSON)")
    parser.add_argument("-rdv", dest="rdv_alias", type=str, required=True, help="Type de RDV alias (ex: m6, p6)")
    parser.add_argument("-prat", dest="prat_alias", type=str, required=False, help="Praticien alias (ex: criton)")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    cfg = load_config()

    rdv_map = cfg.rdv_aliases.get(args.rdv_alias)
    if not rdv_map:
        raise SystemExit(f"Alias RDV inconnu: {args.rdv_alias}")
    visit_id = int(rdv_map["visit_motive_ids"])
    agenda_id = int(rdv_map["agenda_ids"])

    prat_id: Optional[int] = None
    if args.prat_alias:
        prat_id = cfg.prat_aliases.get(args.prat_alias)
        if prat_id is None:
            raise SystemExit(f"Alias praticien inconnu: {args.prat_alias}")

    # Search window
    start = date.today()
    search_end = start + timedelta(days=30 * max(1, cfg.months))

    prev_notified = load_notified()
    current_found_keys: set[str] = set()
    current_start = start

    while current_start <= search_end:
        try:
            resp = fetch_availabilities(
                base_url=cfg.base_url,
                visit_motive_ids=visit_id,
                agenda_ids=agenda_id,
                practice_ids=prat_id,
                start_date=current_start,
                limit=cfg.limit,
                telehealth=False,
                master_patient_signed_id=cfg.master_patient_signed_id,
                debug=cfg.debug,
            )
        except Exception as e:
            print(f"Erreur d'appel API: {e}")
            return

        if resp.get("reason") == "not_opened_availability":
            print("Les dates ne sont pas encore ouvertes à la réservation. Arrêt.")
            break

        availabilities = resp.get("availabilities") or []
        for day in availabilities:
            for slot_iso in day.get("slots", []) or []:
                key = make_key(prat_id, visit_id, agenda_id, slot_iso)
                current_found_keys.add(key)
                if key not in prev_notified:
                    day_txt, time_txt = _format_slot_french(slot_iso)
                    rdv_label = cfg.rdv_labels.get(args.rdv_alias, args.rdv_alias)
                    prat_label = (
                        cfg.prat_labels.get(args.prat_alias, args.prat_alias)
                        if args.prat_alias
                        else ""
                    )
                    suffix = f" pour {prat_label}" if prat_label else ""
                    message = f"{day_txt} à {time_txt} les {rdv_label}{suffix}"
                    notify(message)

        current_start = _advance_to_next_start(resp, current_start)

    # End of scan window: overwrite store with the complete set from this run
    write_notified(current_found_keys)
    print(f"Scan terminé. {len(current_found_keys)} créneau(x) trouvé(s) pour baseline suivante.")
