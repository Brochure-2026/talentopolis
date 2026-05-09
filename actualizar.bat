@echo off
echo ======================================================
echo   ACTUALIZADOR DE CONTENIDOS - TALENTOPOLIS
echo ======================================================
echo.
echo [*] Sincronizando textos_talentopolis.txt con index.html...
python sync_textos.py
echo.
echo [*] Proceso finalizado.
pause
