from __future__ import annotations

import shutil
import subprocess
from typing import Optional


def notify(message: str, *, title: str = "Créneau trouvé") -> None:
    """Send a notification if Termux is available; fallback to console output."""
    if shutil.which("termux-notification"):
        try:
            subprocess.run(
                [
                    "termux-notification",
                    "--title",
                    title,
                    "--content",
                    message,
                ],
                check=False,
            )
            return
        except Exception:
            pass

    print(f"[Notification] {title}: {message}")
