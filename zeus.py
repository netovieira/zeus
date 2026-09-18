#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

# Garante que a saída fique na ordem certa mesmo quando redirecionada
# (pipe/arquivo), inclusive intercalada com o output de subprocessos
# como "athena.py"/"claude" chamados com capture=False.
sys.stdout.reconfigure(line_buffering=True)

_ENTRY_PATH = Path(__file__).resolve()
_SRC_DIR = _ENTRY_PATH.parent / "src"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from zeus.cli import main

if __name__ == "__main__":
    main(_ENTRY_PATH)
