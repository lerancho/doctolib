from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta
from typing import Optional

from .availability import filter_slots
from .providers.file_json import load_slots_from_file
from .providers.http_doctolib import fetch_availabilities, API_DEFAULT_URL
from .storage import load_notified, mark_notified, make_key
from .notify import notify


RDV_ALIASES = {
    # Provided examples
    "m6": {"visit_motive_ids": 6425744, "agenda_ids": 942956},
    "p6": {"visit_motive_ids": 6425745, "agenda_ids": 942956},
}

PRAT_ALIASES = {
    # Example mapping from spec
    "criton": 6425745,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Outil pour vérifier des créneaux disponibles dans les prochains mois."
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    # Default hello
    parser.add_argument("--hello", action="store_true", help="Affiche Hello Termux.")

    # Check local JSON
    check = sub.add_parser("check", help="Vérifie des disponibilités depuis un fichier JSON local")
    check.add_argument("--file", type=str, required=True)
    check.add_argument("--months", type=int, default=2)
    check.add_argument("--from", dest="from_date", type=str, default=None)

    # Scan remote API (Doctolib-style)
    scan = sub.add_parser("scan", help="Scanne l'API de disponibilités distante")
    scan.add_argument("-rdv", dest="rdv_alias", type=str, required=True, help="Type de RDV alias (ex: m6, p6)")
    scan.add_argument("-prat", dest="prat_alias", type=str, required=False, help="Praticien alias (ex: criton)")
    scan.add_argument("--visit", dest="visit_motive_ids", type=int, required=False, help="Override visit_motive_ids")
    scan.add_argument("--agenda", dest="agenda_ids", type=int, required=False, help="Override agenda_ids")
    scan.add_argument("--practice", dest="practice_ids", type=int, required=False, help="Override practice_ids")
    scan.add_argument("--months", type=int, default=6, help="Durée de recherche en mois")
    scan.add_argument("--start", dest="start_date", type=str, default=None, help="Date de départ YYYY-MM-DD (défaut: aujourd'hui)")
    scan.add_argument("--limit", type=int, default=15, help="Paramètre limit (max 15)")
    scan.add_argument("--base-url", type=str, default=API_DEFAULT_URL, help="URL de l'API")
    scan.add_argument("--signed", dest="master_patient_signed_id", type=str, default=None, help="master_patient_signed_id si requis")

    return parser.parse_args()


def _resolve_ids(args: argparse.Namespace) -> tuple[Optional[int], int, int]:
    rdv_map = RDV_ALIASES.get(args.rdv_alias, {})
    visit = args.visit_motive_ids if args.visit_motive_ids is not None else rdv_map.get("visit_motive_ids")
    agenda = args.agenda_ids if args.agenda_ids is not None else rdv_map.get("agenda_ids")
    prat = args.practice_ids if args.practice_ids is not None else (PRAT_ALIASES.get(args.prat_alias) if args.prat_alias else None)
    if visit is None or agenda is None:
        raise SystemExit("Alias RDV inconnu et aucune valeur override fournie (visit/agenda).")
    return prat, int(visit), int(agenda)


def _date_from_str_or_today(s: Optional[str]) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date() if s else date.today()


def _advance_to_next_start(resp: dict, current_start: date) -> date:
    next_slot = resp.get("next_slot")
    if next_slot:
        try:
            dt = datetime.fromisoformat(next_slot.replace("Z", "+00:00"))
            return dt.date()
        except Exception:
            pass
    # If no next_slot, advance to the day after the last availability date in the response
    av = resp.get("availabilities") or []
    last_date = None
    for item in av:
        try:
            last_date = datetime.strptime(item.get("date"), "%Y-%m-%d").date()
        except Exception:
            continue
    return (last_date or current_start) + timedelta(days=1)


def main() -> None:
    args = _parse_args()

    if args.cmd is None:
        print("Hello, Termux!")
        return

    if args.cmd == "check":
        start_dt = datetime.strptime(args.from_date, "%Y-%m-%d") if args.from_date else datetime.now()
        end_dt = start_dt + timedelta(days=30 * max(1, args.months))
        slots = load_slots_from_file(args.file)
        selected = filter_slots(slots, start=start_dt, end=end_dt)
        if not selected:
            print("Aucun créneau disponible dans la période demandée.")
            return
        print(f"Créneaux disponibles entre {start_dt:%Y-%m-%d} et {end_dt:%Y-%m-%d}:")
        for s in selected:
            print(f"- {s.start:%Y-%m-%d %H:%M} → {s.end:%H:%M}")
        return

    if args.cmd == "scan":
        prat_id, visit_id, agenda_id = _resolve_ids(args)
        months = max(1, args.months)
        search_end = _date_from_str_or_today(args.start_date) + timedelta(days=30 * months)
        current_start = _date_from_str_or_today(args.start_date)

        notified = load_notified()

        while current_start <= search_end:
            try:
                resp = fetch_availabilities(
                    base_url=args.base_url,
                    visit_motive_ids=visit_id,
                    agenda_ids=agenda_id,
                    practice_ids=prat_id,
                    start_date=current_start,
                    limit=args.limit,
                    telehealth=False,
                    master_patient_signed_id=args.master_patient_signed_id,
                )
            except Exception as e:
                print(f"Erreur d'appel API: {e}")
                return

            # Stop if not opened
            if resp.get("reason") == "not_opened_availability":
                print("Les dates ne sont pas encore ouvertes à la réservation. Arrêt.")
                return

            # Collect slots and alert once for a new slot
            availabilities = resp.get("availabilities") or []
            found_new = False
            for day in availabilities:
                for slot_iso in day.get("slots", []) or []:
                    key = make_key(prat_id, visit_id, agenda_id, slot_iso)
                    if key not in notified:
                        message = f"Slot: {slot_iso} (practice={prat_id or '-'}, visit={visit_id}, agenda={agenda_id})"
                        notify(message)
                        mark_notified(key)
                        print("Nouvelle disponibilité trouvée et notifiée. Arrêt.")
                        found_new = True
                        break
                if found_new:
                    break
            if found_new:
                return

            # Advance start date
            current_start = _advance_to_next_start(resp, current_start)


if __name__ == "__main__":
    main()
