@echo off
cd /d "%~dp0"
py -3.13 -c "import sys; assert sys.version_info[:2] == (3,13)" >nul 2>&1
if not errorlevel 1 (
  py -3.13 -m venv .venv
  goto instalar
)
py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12)" >nul 2>&1
if not errorlevel 1 (
  py -3.12 -m venv .venv
  goto instalar
)
python -c "import sys; assert sys.version_info[:2] in [(3,12),(3,13)]" >nul 2>&1
if errorlevel 1 goto falha
python -m venv .venv
:instalar
if not exist ".venv\Scripts\python.exe" goto falha
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto falha
echo Preparacao concluida. Abra ABRIR-APRESENTACAO.cmd.
pause
exit /b 0
:falha
echo Nao foi possivel preparar. E necessario Python 3.12 ou 3.13 e internet.
pause
exit /b 1
