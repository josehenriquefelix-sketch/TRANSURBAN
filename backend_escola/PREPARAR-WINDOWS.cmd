@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo TRANSURBAN - preparar antes da apresentacao, com internet.
py -3.12 iniciar_apresentacao.py --preparar
if errorlevel 1 goto falha
py -3.12 iniciar_apresentacao.py --testar
if errorlevel 1 goto falha
py -3.12 iniciar_apresentacao.py --evidencias
if errorlevel 1 goto falha
echo.
echo Preparacao e verificacoes concluidas. Para iniciar, abra APRESENTAR-WINDOWS.cmd.
pause
exit /b 0
:falha
echo.
echo A preparacao nao foi concluida. Confira a mensagem acima. Requer Python 3.12 e internet.
echo Nao apague o banco ou o arquivo .env. Envie somente o erro, sem credenciais.
pause
exit /b 1
