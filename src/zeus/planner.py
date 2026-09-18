from __future__ import annotations

import os
from pathlib import Path

from zeus.athena_bridge import run_athena_index
from zeus.claude_client import call_claude
from zeus.collector import collect_summaries
from zeus.prompts import PLAN_PROMPT
from zeus.settings import ZEUS_PLAN_DIRNAME, ZEUS_PLAN_FILENAME
from zeus.system.backup import backup_file
from zeus.system.process import timestamp


def validate_plan(content: str) -> bool:

    stripped = content.strip()

    if len(stripped) < 200:
        print(
            "[ERROR] Generated plan is suspiciously small."
        )
        return False

    # Evita que uma resposta acidental venha embrulhada em
    # markdown fence.
    if stripped.startswith("```"):
        print(
            "[ERROR] Generated plan contains unexpected markdown "
            "fences."
        )
        return False

    return True


def run_plan(
    task: str,
    project_root: Path,
    entry_path: Path,
) -> bool:

    if not run_athena_index(entry_path, project_root):
        print(
            "[WARN] Não foi possível atualizar o índice da Athena."
        )
        print(
            "[WARN] Planejamento abortado."
        )
        return False

    summaries = collect_summaries(project_root)

    if summaries is None:
        print(
            "[ERROR] Nenhum índice da Athena encontrado em "
            f"{project_root} mesmo após tentar indexar."
        )
        return False

    print()
    print("=" * 70)
    print("Zeus — planejando com o Claude")
    print("=" * 70)

    prompt = PLAN_PROMPT.format(
        task=task,
        summaries=summaries,
    )

    plan = call_claude(prompt)

    if plan is None:
        print(
            "[WARN] Planejamento falhou."
        )
        return False

    if not validate_plan(plan):
        print(
            "[WARN] Validação falhou; plano não foi salvo."
        )
        return False

    claude_dir = project_root / ZEUS_PLAN_DIRNAME
    claude_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    plan_path = claude_dir / ZEUS_PLAN_FILENAME

    if plan_path.exists():
        backup_file(
            plan_path,
            prefix=plan_path.stem,
        )

    # Substituição atômica-ish: escreve um temporário no mesmo
    # diretório e depois substitui.
    temporary = plan_path.with_name(
        f".{ZEUS_PLAN_FILENAME}.tmp_{timestamp()}"
    )

    try:

        temporary.write_text(
            plan.strip() + "\n",
            encoding="utf-8",
        )

        os.replace(
            temporary,
            plan_path,
        )

    except Exception as exc:

        print(
            f"[ERROR] Could not write plan: {exc}"
        )

        if temporary.exists():
            temporary.unlink()

        return False

    print(
        f"\n[OK] Plano salvo em: {plan_path}"
    )
    print(
        "[INFO] Revise o plano antes de seguir — é um candidato a "
        "verificar, não uma verdade absoluta."
    )

    return True
