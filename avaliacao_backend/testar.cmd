@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe exit /b 1
.venv\Scripts\python.exe -m unittest discover -s tests -v
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe scripts\exportar_ia.py
if errorlevel 1 exit /b 1
.venv\Scripts\python.exe scripts\capturar_http.py
