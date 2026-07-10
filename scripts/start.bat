@echo off
chcp 65001 >nul
title AI Maturity Platform - Запуск
echo.
echo === AI Maturity Platform - Запуск ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
