@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente Python nao encontrado. Siga o roteiro de instalacao.
  pause
  exit /b 1
)
set "PYTHONUTF8=1"
".venv\Scripts\python.exe" "configurar_supabase.py" --transurban
set "result=%errorlevel%"
echo.
if not "%result%"=="0" echo A conexao nao foi configurada. Confira os dados antes de tentar novamente.
pause
exit /b %result%
