@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" iniciar.py
) else if exist "C:\Users\josep\Documents\TRANSURBAN\venv\Scripts\python.exe" (
  "C:\Users\josep\Documents\TRANSURBAN\venv\Scripts\python.exe" iniciar.py
) else (
  py iniciar.py
)
if errorlevel 1 pause
