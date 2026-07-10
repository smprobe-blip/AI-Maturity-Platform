@echo off
chcp 65001 >nul
title AI Maturity Platform - Статус
echo.
echo === AI Maturity Platform - Статус ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0status.ps1"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
