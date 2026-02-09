@echo off
title Persona Træningsplatform
echo.
echo   Persona Traeningsplatform
echo   Installerer dependencies...
echo.
pip install flask anthropic >nul 2>&1
echo   Starter server...
echo   Browseren aabner automatisk.
echo   Luk dette vindue for at stoppe.
echo.
start http://localhost:5000
python web.py
