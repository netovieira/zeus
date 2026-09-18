from __future__ import annotations

import sys


def confirm(
    question: str,
    *,
    default: bool = False,
) -> bool:
    """
    Pergunta y/n ao usuario. Em sessao nao interativa (stdin sem
    tty — ex.: agente de IA rodando o script), retorna "default"
    sem bloquear esperando input.
    """

    if not sys.stdin.isatty():
        return default

    suffix = "[Y/n]" if default else "[y/N]"

    try:
        answer = input(f"{question} {suffix}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return default

    if not answer:
        return default

    return answer in ("y", "yes", "s", "sim")
