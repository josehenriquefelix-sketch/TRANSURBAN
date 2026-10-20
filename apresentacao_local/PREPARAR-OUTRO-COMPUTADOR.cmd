@echo off
cd /d "%~dp0"
py -m venv .venv
if errorlevel 1 goto falha
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto falha
echo Preparacao concluida. Abra ABRIR-APRESENTACAO.cmd.
pause
exit /b 0
:falha
echo Nao foi possivel preparar. E necessario Python 3.12 ou 3.13 e internet.
pause
exit /b 1
