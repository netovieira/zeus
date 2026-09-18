from __future__ import annotations

import shutil
from pathlib import Path

from zeus.system.process import timestamp


def backup_file(
    path: Path,
    prefix: str | None = None,
) -> Path | None:

    if not path.exists():
        return None

    if prefix is None:
        prefix = path.stem

    backup = path.with_name(
        f"{prefix}.backup_{timestamp()}{path.suffix}"
    )

    shutil.copy2(
        path,
        backup,
    )

    print(
        f"[OK] Backup created: {backup}"
    )

    return backup
