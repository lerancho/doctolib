from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_LOCATIONS = [
    Path("config.json"),
]


@dataclass
class Config:
    base_url: str
    master_patient_signed_id: Optional[str]
    months: int
    limit: int
    rdv_aliases: Dict[str, Dict[str, int]]
    prat_aliases: Dict[str, int]
    debug: bool = False
    rdv_labels: Dict[str, str] = None  # Optional friendly names
    prat_labels: Dict[str, str] = None


def _load_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_config(explicit_path: Optional[str] = None) -> Config:
    paths: list[Path] = []
    if explicit_path:
        paths.append(Path(explicit_path))
    paths.extend(DEFAULT_LOCATIONS)

    loaded: Dict[str, Any] = {}
    for p in paths:
        if p.exists():
            try:
                loaded = _load_json(p)
                break
            except Exception:
                continue

    # Defaults with safe fallbacks
    base_url = str(loaded.get("base_url", "https://www.doctolib.fr/availabilities.json"))
    signed = loaded.get("master_patient_signed_id")
    months = int(loaded.get("months", 6))
    limit = max(1, min(int(loaded.get("limit", 15)), 15))
    rdv_aliases = loaded.get("rdv_aliases") or {}
    prat_aliases = loaded.get("prat_aliases") or {}
    rdv_labels = loaded.get("rdv_labels") or {}
    prat_labels = loaded.get("prat_labels") or {}
    debug = bool(loaded.get("debug", False) or os.environ.get("HELLOTERMUX_DEBUG") in {"1", "true", "TRUE", "yes", "on"})

    # Provide sensible defaults matching the spec if not overridden
    if not rdv_aliases:
        rdv_aliases = {
            "m6": {"visit_motive_ids": 6425744, "agenda_ids": 942956},
            "p6": {"visit_motive_ids": 6425745, "agenda_ids": 942956},
        }
    if not prat_aliases:
        prat_aliases = {
            "criton": 6425745,
        }
    if not rdv_labels:
        rdv_labels = {
            "m6": "moins de 6 ans",
            "p6": "plus de 6 ans",
        }
    if not prat_labels:
        prat_labels = {
            "criton": "Criton",
        }

    return Config(
        base_url=base_url,
        master_patient_signed_id=signed,
        months=months,
        limit=limit,
        rdv_aliases=rdv_aliases,
        prat_aliases=prat_aliases,
        debug=debug,
        rdv_labels=rdv_labels,
        prat_labels=prat_labels,
    )
