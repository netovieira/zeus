from __future__ import annotations

import argparse
import sys
from pathlib import Path

from zeus.planner import run_plan

HELP_EPILOG = r"""
REQUISITOS
    Python 3.10+
    Claude Code instalado e autenticado ("claude -p")
    git (para instalar/atualizar a Athena automaticamente, se necessario)

COMANDOS
    plan "<tarefa>" [PASTA]
                       Planeja a tarefa descrita usando o indice de
                       arquitetura da Athena (.athena/). Roda
                       "athena index" automaticamente antes de
                       planejar (o cache incremental da Athena faz
                       reindexacoes repetidas serem baratas), pede ao
                       Claude para escolher os arquivos relevantes a
                       partir dos resumos, e escreve o plano em
                       .claude/zeus-plan.md (PASTA padrao: pasta
                       atual).
    -h, --help         Mostra esta ajuda e sai.

COMO FUNCIONA
    O Zeus nao le codigo-fonte diretamente: ele cruza a descricao da
    tarefa com os resumos ja gerados pela Athena
    (github.com/netovieira/athena) e pede ao Claude Code ("claude -p")
    para escolher os arquivos candidatos e escrever um plano de acao.
    O resultado (.claude/zeus-plan.md) e um ponto de partida a
    verificar, nao uma verdade absoluta.

ATHENA
    Precisa da Athena instalada. Procura athena.py na variavel de
    ambiente ZEUS_ATHENA_PATH, numa pasta irma "athena/" (layout do
    monorepo myscripts), ou numa copia gerenciada em
    ~/.thero/tools/athena (compartilhada com o thero) — clonando ou
    atualizando via git automaticamente, com confirmacao, se
    necessario e o terminal for interativo. Em sessao nao interativa
    (ex.: agente de IA), pula o clone/update automatico em vez de
    travar esperando confirmacao.

EXEMPLOS
    python zeus.py plan "adicionar campo de telefone no cadastro de usuario"
    python zeus.py plan "corrigir bug de paginacao" /caminho/do/projeto
    python zeus.py --help
"""


def parse_args() -> argparse.Namespace:

    parser = argparse.ArgumentParser(
        prog="zeus.py",
        description=(
            "Planejador que cruza uma tarefa com o indice de "
            "arquitetura da Athena para decidir quais arquivos "
            "importam (via Claude Code)."
        ),
        epilog=HELP_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    plan_parser = subparsers.add_parser(
        "plan",
        help="Gera um plano de acao para uma tarefa.",
    )
    plan_parser.add_argument(
        "task",
        help="Descricao da tarefa a planejar.",
    )
    plan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Pasta do projeto a planejar (padrao: pasta atual).",
    )

    return parser.parse_args()


def main(entry_path: Path) -> None:

    args = parse_args()

    if args.command == "plan":

        project_root = Path(args.path).resolve()

        if not project_root.is_dir():
            print(
                f"[ERROR] Pasta nao encontrada: {project_root}"
            )
            sys.exit(1)

        if not run_plan(args.task, project_root, entry_path):
            sys.exit(1)

    else:
        print(
            "Uso: python zeus.py plan \"<tarefa>\" [pasta] "
            "(--help para detalhes)"
        )
        sys.exit(1)
