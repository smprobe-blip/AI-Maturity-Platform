#Requires -Version 5.1
<#
.SYNOPSIS
    Перезапуск AI Maturity Platform.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptsDir = "C:\Projects\AI-Maturity-Platform\scripts"

Write-Host "`n=== Перезапуск AI Maturity Platform ===" -ForegroundColor Cyan

# Остановка
Write-Host "`n[1/2] Остановка..." -ForegroundColor Yellow
& (Join-Path $ScriptsDir "stop.ps1")

Start-Sleep -Seconds 3

# Запуск
Write-Host "`n[2/2] Запуск..." -ForegroundColor Yellow
& (Join-Path $ScriptsDir "start.ps1")
