@echo off
chcp 65001 >nul
:loop
cls
echo ====================================
echo    AI_FRIENT_BOT ЗАПУСКАЕТСЯ...
echo ====================================
python mibot.py
echo.
echo [!] Бот отключился. Перезапуск через 5 сек...
timeout /t 5
goto loop