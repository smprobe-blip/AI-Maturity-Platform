@echo off
chcp 65001 >nul
title AI Maturity Platform - Перезапуск
echo.
echo === AI Maturity Platform - Перезапуск ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart.ps1"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
