@echo off
setlocal
cd /d "%~dp0"

echo === TRANSURBAN: iniciar telas e API ===
where python >nul 2>nul
if errorlevel 1 (
  echo Python nao encontrado. Instale Python 3.10 ou superior e marque Add Python to PATH.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo Criando ambiente virtual...
  python -m venv backend\.venv
  if errorlevel 1 goto erro
)

if not exist "backend\.env" (
  copy "backend\.env.example" "backend\.env" >nul
  echo Foi criado backend\.env a partir do exemplo.
)

findstr /r /c:"^SUPABASE_KEY=$" /c:"^SUPABASE_KEY=sb_secret_EXEMPLO_FICTICIO_NAO_FUNCIONA$" "backend\.env" >nul
if not errorlevel 1 (
  echo Preencha SUPABASE_KEY com a chave secreta deste projeto. Ela deve ficar apenas no backend\.env local.
  start /wait notepad.exe "backend\.env"
  echo Pressione uma tecla para continuar; sem chave o CRUD remoto nao funcionara.
  pause >nul
)

echo Conferindo dependencias...
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 goto erro

start "TRANSURBAN API - mantenha aberto" cmd /k "cd /d ""%CD%"" && ""backend\.venv\Scripts\python.exe"" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
start "TRANSURBAN frontend - mantenha aberto" cmd /k "cd /d ""%CD%"" && python -m http.server 5500 --directory frontend"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5500/"
echo As telas foram abertas. Nao feche as duas janelas de terminal enquanto estiver usando o sistema.
exit /b 0

:erro
echo Nao foi possivel preparar o ambiente. Confira a instalacao do Python e a conexao com a internet.
pause
exit /b 1




