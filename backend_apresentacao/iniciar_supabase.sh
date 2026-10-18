#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "$0")"
export TRANSURBAN_MODO=supabase
exec bash iniciar.sh
