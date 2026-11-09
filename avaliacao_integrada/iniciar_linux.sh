#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r backend/requirements.txt
if [ "${1:-}" = "--demo" ]; then
 export TRANSURBAN_DEMO=1
 echo 'ENSAIO LOCAL: SQLite. Não é a comprovação do Supabase.'
else
 export TRANSURBAN_DEMO=0
 if [ ! -f backend/.env ]; then
   cp backend/.env.example backend/.env
   echo 'Preencha SUPABASE_URL e SUPABASE_KEY em backend/.env e execute novamente.'
   exit 1
 fi
fi
exec .venv/bin/python backend/abrir_app.py
