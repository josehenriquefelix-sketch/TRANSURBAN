@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto executar
where py >nul 2>nul
if errorlevel 1 goto tentar_python
py preparar.py
if errorlevel 1 goto falha
goto executar
:tentar_python
where python >nul 2>nul
if errorlevel 1 goto sem_python
python preparar.py
if errorlevel 1 goto falha
:executar
".venv\Scripts\python.exe" abrir_apresentacao.py %*
if errorlevel 1 goto falha
exit /b 0
:sem_python
echo Instale Python 3.11 ou mais recente com o responsavel pelo notebook.
:falha
echo Confira a mensagem acima. A primeira preparacao precisa de internet.
pause
exit /b 1
