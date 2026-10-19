@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo TRANSURBAN - apresentacao local, sem Supabase.
echo Depois de Application startup complete, digite no Chrome deste notebook:
echo http://127.0.0.1:8000/docs
echo Mantenha esta janela aberta. Ctrl+C encerra a API.
py -3.12 iniciar_apresentacao.py
pause
