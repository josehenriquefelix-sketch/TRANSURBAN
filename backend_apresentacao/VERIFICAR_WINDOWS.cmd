@echo off
cd /d "%~dp0"
py preparar.py --testes
if errorlevel 1 (
  echo A preparacao nao terminou. Confira a mensagem acima.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 (
  echo A verificacao encontrou uma falha.
  pause
  exit /b 1
)
echo VERIFICACAO APROVADA. Agora execute iniciar.cmd.
pause
