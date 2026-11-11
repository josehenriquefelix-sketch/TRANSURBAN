@echo off
setlocal
cd /d "%~dp0"
if not exist "backend\.venv\Scripts\python.exe" (
  echo Execute INICIAR_TRANSURBAN.cmd primeiro para preparar o ambiente.
  pause
  exit /b 1
)
backend\.venv\Scripts\python.exe verificar_ambiente.py
set "resultado_verificacao=%errorlevel%"
pause
exit /b %resultado_verificacao%
