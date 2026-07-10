@echo off
chcp 65001 >nul
title AI Maturity Platform - Логи
echo.
echo === AI Maturity Platform - Логи ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0logs.ps1"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
