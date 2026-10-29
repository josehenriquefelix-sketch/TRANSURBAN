@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
  where python >nul 2>nul
  if errorlevel 1 (
    echo Python 3.10 ou superior nao foi encontrado.
    echo Instale Python marcando Add Python to PATH e tente novamente.
    pause
    exit /b 1
  )
  echo Preparando o ambiente na primeira abertura...
  python -m venv backend\.venv
  if errorlevel 1 goto erro
)

if not exist "backend\.env" copy "backend\.env.example" "backend\.env" >nul

findstr /c:"SUPABASE_URL=https://SEU_PROJETO.supabase.co" "backend\.env" >nul
if not errorlevel 1 goto configurar
findstr /r /c:"^SUPABASE_KEY=$" /c:"^SUPABASE_KEY=sb_secret_EXEMPLO_FICTICIO_NAO_FUNCIONA$" "backend\.env" >nul
if not errorlevel 1 goto configurar
goto pronto

:configurar
echo Configure a URL do projeto e a chave privada no arquivo que sera aberto.
echo A chave fica somente neste computador e nao deve ser enviada ao GitHub.
start /wait notepad.exe "backend\.env"

:pronto
backend\.venv\Scripts\python.exe -c "import fastapi, uvicorn, pandas, dotenv, supabase" >nul 2>nul
if errorlevel 1 (
  echo Instalando dependencias necessarias...
  backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
  if errorlevel 1 goto erro
)

backend\.venv\Scripts\python.exe backend\abrir_app.py
if errorlevel 1 goto erro
exit /b 0

:erro
echo Nao foi possivel iniciar. Confira a janela de mensagens e tente novamente.
pause
exit /b 1

