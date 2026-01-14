from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List


@dataclass(frozen=True)
class Slot:
    start: datetime
    end: datetime


def filter_slots(slots: Iterable[Slot], start: datetime, end: datetime) -> List[Slot]:
    return [s for s in slots if s.start >= start and s.end <= end]
