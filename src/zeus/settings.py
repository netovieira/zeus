from __future__ import annotations

# Layout de saída da Athena (consumido, não gerado pelo Zeus).
OUTPUT_DIRNAME = ".athena"

TREE_DIRNAME = "tree"

ROOT_SUMMARY_FILENAME = "summary.md"

# Onde o plano gerado é escrito no projeto do usuário.
ZEUS_PLAN_DIRNAME = ".claude"

ZEUS_PLAN_FILENAME = "zeus-plan.md"

# Trava de segurança: trunca o contexto enviado ao Claude se os
# resumos combinados excederem isso (projetos muito grandes).
MAX_CONTEXT_CHARS = 60_000

ATHENA_PATH_ENV_VAR = "ZEUS_ATHENA_PATH"

ATHENA_REPO_URL = "https://github.com/netovieira/athena.git"

ATHENA_ENTRY_SCRIPT = "athena.py"
