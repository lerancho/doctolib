from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import date
from typing import Any, Dict, Optional


API_DEFAULT_URL = "https://www.doctolib.fr/availabilities.json"


def _mask_params(params: Dict[str, Any]) -> Dict[str, Any]:
    masked = dict(params)
    if "master_patient_signed_id" in masked and masked["master_patient_signed_id"]:
        masked["master_patient_signed_id"] = "***"
    return masked


def fetch_availabilities(
    base_url: str,
    *,
    visit_motive_ids: int,
    agenda_ids: int,
    practice_ids: Optional[int],
    start_date: date,
    limit: int = 15,
    telehealth: bool = False,
    master_patient_signed_id: Optional[str] = None,
    debug: bool = False,
) -> Dict[str, Any]:
    """
    Call the remote availabilities endpoint and return the parsed JSON.
    Keeps dependencies stdlib-only for Termux compatibility.
    """
    params: Dict[str, Any] = {
        "visit_motive_ids": str(visit_motive_ids),
        "agenda_ids": str(agenda_ids),
        "telehealth": "true" if telehealth else "false",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "limit": str(max(1, min(limit, 15))),
    }
    if practice_ids is not None:
        params["practice_ids"] = str(practice_ids)
    if master_patient_signed_id:
        params["master_patient_signed_id"] = master_patient_signed_id

    url = base_url or API_DEFAULT_URL
    qs = urllib.parse.urlencode(params)
    full_url = f"{url}?{qs}"

    req = urllib.request.Request(
        full_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "hellotermux/0.1 (+termux; stdlib)",
        },
        method="GET",
    )
    if debug:
        print("[HTTP] GET", url)
        print("[HTTP] Params:", _mask_params(params))

    with urllib.request.urlopen(req, timeout=20) as resp:
        status = getattr(resp, "status", None) or resp.getcode()
        data = resp.read().decode("utf-8")
        parsed = json.loads(data)
        if debug:
            print(f"[HTTP] Status: {status}")
            try:
                print("[HTTP] JSON:")
                print(json.dumps(parsed, ensure_ascii=False, indent=2))
            except Exception:
                # Fallback raw data if pretty print fails
                print(data)
        return parsed
