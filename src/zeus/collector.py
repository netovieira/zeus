from __future__ import annotations

from pathlib import Path

from zeus.settings import (
    MAX_CONTEXT_CHARS,
    OUTPUT_DIRNAME,
    ROOT_SUMMARY_FILENAME,
    TREE_DIRNAME,
)


def collect_summaries(project_root: Path) -> str | None:
    """
    Concatena o resumo raiz e todos os resumos de arquivo/pasta já
    indexados pela Athena (.athena/summary.md e .athena/tree/**) num
    único bloco de texto, para servir de contexto ao Claude. Trunca
    se ultrapassar MAX_CONTEXT_CHARS, sinalizando o corte em vez de
    falhar silenciosamente.
    """

    output_dir = project_root / OUTPUT_DIRNAME
    root_summary_path = output_dir / ROOT_SUMMARY_FILENAME
    tree_dir = output_dir / TREE_DIRNAME

    if not root_summary_path.exists():
        return None

    parts = [
        "## Resumo raiz do projeto\n\n"
        + root_summary_path.read_text(
            encoding="utf-8", errors="replace"
        ).strip()
    ]

    if tree_dir.is_dir():

        summary_files = sorted(tree_dir.rglob("*.md"))

        for summary_file in summary_files:

            relative = summary_file.relative_to(tree_dir)

            if summary_file.name == "_dir_summary.md":
                target = str(relative.parent).replace("\\", "/") or "."
            else:
                target = str(relative.with_suffix("")).replace("\\", "/")

            text = summary_file.read_text(
                encoding="utf-8", errors="replace"
            ).strip()

            parts.append(f"## {target}\n\n{text}")

    combined = "\n\n".join(parts)

    if len(combined) > MAX_CONTEXT_CHARS:
        combined = (
            combined[:MAX_CONTEXT_CHARS]
            + "\n\n[TRUNCADO: resumos excederam o limite de contexto]"
        )

    return combined
