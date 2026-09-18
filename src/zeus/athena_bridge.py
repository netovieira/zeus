from __future__ import annotations

import os
import sys
from pathlib import Path

from zeus.settings import (
    ATHENA_ENTRY_SCRIPT,
    ATHENA_PATH_ENV_VAR,
    ATHENA_REPO_URL,
)
from zeus.system.process import run_command
from zeus.system.tool_repo import ensure_tool_repo


def find_athena_script(entry_path: Path) -> Path | None:
    """
    Localiza o athena.py. Ordem:

    1. Variável de ambiente ZEUS_ATHENA_PATH (caminho explícito para
       o athena.py).
    2. Pasta irmã "athena/athena.py", assumindo o layout padrão do
       monorepo myscripts (zeus/ e athena/ lado a lado).
    3. Cópia gerenciada em "~/.thero/tools/athena" — clonada (ou
       atualizada, se desatualizada) automaticamente via git, com
       confirmação do usuário. Compartilhada com o thero: se ele já
       clonou a Athena ali, o Zeus reaproveita em vez de duplicar.
    """

    env_path = os.environ.get(ATHENA_PATH_ENV_VAR)

    if env_path:
        candidate = Path(env_path).expanduser()
        return candidate if candidate.is_file() else None

    sibling = entry_path.parent.parent / "athena" / "athena.py"

    if sibling.is_file():
        return sibling

    return ensure_tool_repo(
        "athena",
        ATHENA_REPO_URL,
        ATHENA_ENTRY_SCRIPT,
    )


def run_athena_index(entry_path: Path, project_root: Path) -> bool:
    """
    Roda "athena index <project_root>" antes de planejar. O cache
    incremental da própria Athena (.athena/manifest.json) faz
    reindexações repetidas serem baratas quando nada mudou, então
    isto roda sempre, sem checagem própria de "está desatualizado".
    """

    athena_script = find_athena_script(entry_path)

    if athena_script is None:
        print(
            "[ERROR] athena.py não disponível. Rode este comando "
            "num terminal interativo para permitir a instalação "
            "automática, instale a Athena "
            "(https://github.com/netovieira/athena) manualmente na "
            "pasta irmã de zeus (ex.: ~/.myscripts/athena), ou "
            f"defina a variável de ambiente {ATHENA_PATH_ENV_VAR} "
            "apontando para o athena.py."
        )
        return False

    print()
    print("=" * 70)
    print("Athena — atualizando índice antes de planejar")
    print("=" * 70)

    sys.stdout.flush()

    result = run_command(
        [
            "python",
            str(athena_script),
            "index",
            str(project_root),
        ],
        capture=False,
    )

    return result.returncode == 0
