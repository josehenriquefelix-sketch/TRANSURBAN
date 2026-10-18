#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "$0")"
echo 'Abra http://127.0.0.1:8000/apresentacao'
exec .venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
