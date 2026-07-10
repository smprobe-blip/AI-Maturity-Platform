@echo off
chcp 65001 >nul
title AI Maturity Platform - Остановка
echo.
echo === AI Maturity Platform - Остановка ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop.ps1"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
