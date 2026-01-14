from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ..availability import Slot


def load_slots_from_file(path: str | Path) -> Iterable[Slot]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    slots = []
    for item in data.get("slots", []):
        try:
            start = datetime.fromisoformat(item["start"])  # e.g. 2026-03-01T10:00:00
            end = datetime.fromisoformat(item["end"])      # e.g. 2026-03-01T10:15:00
            slots.append(Slot(start=start, end=end))
        except Exception:
            # Ignore invalid entries
            continue
    return slots
