from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

from .availability import filter_slots
from .providers.file_json import load_slots_from_file


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Outil simple pour vérifier des créneaux disponibles dans les prochains mois."
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    # Default hello
    parser.add_argument(
        "--hello",
        action="store_true",
        help="Affiche un Hello Termux (par défaut).",
    )

    # Check subcommand
    check = sub.add_parser("check", help="Vérifie les disponibilités depuis un fichier JSON")
    check.add_argument(
        "--file",
        type=str,
        required=True,
        help="Chemin vers un fichier JSON contenant des slots (format {slots: [{start, end}]}).",
    )
    check.add_argument(
        "--months",
        type=int,
        default=2,
        help="Nombre de mois à regarder à partir d'aujourd'hui (défaut: 2).",
    )
    check.add_argument(
        "--from",
        dest="from_date",
        type=str,
        default=None,
        help="Date de début au format YYYY-MM-DD (défaut: aujourd'hui).",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    # Default behavior
    if args.cmd is None:
        print("Hello, Termux!")
        return

    if args.cmd == "check":
        start_date = (
            datetime.strptime(args.from_date, "%Y-%m-%d") if args.from_date else datetime.now()
        )
        end_date = start_date + timedelta(days=30 * max(1, args.months))

        slots = load_slots_from_file(args.file)
        selected = filter_slots(slots, start=start_date, end=end_date)

        if not selected:
            print("Aucun créneau disponible dans la période demandée.")
            return

        print(f"Créneaux disponibles entre {start_date:%Y-%m-%d} et {end_date:%Y-%m-%d}:")
        for s in selected:
            print(f"- {s.start:%Y-%m-%d %H:%M} → {s.end:%H:%M}")


if __name__ == "__main__":
    main()
