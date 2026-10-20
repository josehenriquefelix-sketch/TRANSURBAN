@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo TRANSURBAN - verifica arquivos e abre um servidor temporario.
echo Nao altera seu banco e nao usa Supabase.
py -3.12 iniciar_apresentacao.py --diagnostico
if errorlevel 1 goto falha
echo Confira tambem mapa, permissao de GPS e projetor no equipamento da equipe.
pause
exit /b 0
:falha
echo Diagnostico nao aprovado. Copie a mensagem FALHA sem senhas.
pause
exit /b 1
