#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
mode="${1:-iniciar}"
if [[ "$mode" != iniciar && "$mode" != --testar ]]; then
  printf 'Uso: bash iniciar-linux.sh [--testar]\n' >&2
  exit 2
fi
command -v python3 >/dev/null || { printf 'Python 3 não está instalado. Solicite ao responsável do laboratório.\n' >&2; exit 1; }
# Usa um nome próprio para não conflitar com o arquivo .venv da pasta antiga.
if [[ -e .venv-escola && ! -x .venv-escola/bin/python ]]; then
  printf '.venv-escola já existe, mas não é um ambiente Python válido. Nenhum arquivo foi removido.\n' >&2
  exit 1
fi
if [[ ! -x .venv-escola/bin/python ]]; then
  python3 -m venv .venv-escola || { printf 'Não foi possível criar o ambiente. Confira o pacote python3-venv com o responsável do laboratório.\n' >&2; exit 1; }
fi
py="$PWD/.venv-escola/bin/python"
if [[ "$mode" == --testar ]]; then
  "$py" -m pip install -r requirements-dev.txt
  exec "$py" -m pytest -q
fi
"$py" -m pip install -r requirements.txt
if [[ ! -e .env && ! -L .env && ! -v DATABASE_URL ]]; then
  (umask 077; set -o noclobber; printf '%s\n' 'DATABASE_URL=sqlite:///./transurban_escola.db' > .env)
  printf 'Configuração local criada: SQLite. Não é uma conexão Supabase.\n'
else
  printf 'Configuração de banco existente preservada.\n'
fi
printf '\nDeixe este terminal aberto. Após Application startup complete, abra no mesmo computador:\nhttp://127.0.0.1:8000/docs\nCtrl+C encerra a API.\n\n'
exec "$py" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
