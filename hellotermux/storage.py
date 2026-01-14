from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple


DEFAULT_STORE = Path("data/notified.txt")


def load_notified(store_path: Path = DEFAULT_STORE) -> set[str]:
    if not store_path.exists():
        return set()
    try:
        return set(x.strip() for x in store_path.read_text(encoding="utf-8").splitlines() if x.strip())
    except Exception:
        return set()


def mark_notified(key: str, store_path: Path = DEFAULT_STORE) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as f:
        f.write(key + "\n")


def make_key(practice_id: int | None, visit_motive_ids: int, agenda_ids: int, slot_iso: str) -> str:
    p = str(practice_id) if practice_id is not None else "-"
    return f"{p}|{visit_motive_ids}|{agenda_ids}|{slot_iso}"


def write_notified(keys: Iterable[str], store_path: Path = DEFAULT_STORE) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    # Overwrite the file with the full set from the current run
    with store_path.open("w", encoding="utf-8") as f:
        for k in sorted(set(keys)):
            f.write(k + "\n")
