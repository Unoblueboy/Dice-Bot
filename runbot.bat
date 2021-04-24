@echo off
cd "%~dp0"
CALL env\scripts\activate.bat
python bot.py
