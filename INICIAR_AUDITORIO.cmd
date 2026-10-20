@echo off
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
  echo Execute primeiro: python preparar.py na raiz do projeto, com Python 3.13.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" executar_auditorio.py
pause
