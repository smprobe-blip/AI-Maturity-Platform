#Requires -Version 5.1
<#
.SYNOPSIS
    Просмотр логов AI Maturity Platform.
.PARAMETER Service
    Имя сервиса (backend, frontend, keycloak, baserow, minio, mailhog).
    Если не указан - показываются все логи.
.PARAMETER Tail
    Количество последних строк (по умолчанию 50).
.PARAMETER Follow
    Следить за логами в реальном времени.
.EXAMPLE
    .\logs.ps1
    .\logs.ps1 -Service backend
    .\logs.ps1 -Service backend -Tail 100
    .\logs.ps1 -Follow
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

param(
    [string]$Service = "",
    [int]$Tail = 50,
    [switch]$Follow
)

$ProjectRoot = "C:\Projects\AI-Maturity-Platform"
$InfraDir    = Join-Path $ProjectRoot "infrastructure"

if (-not (Test-Path $InfraDir)) {
    Write-Host "❌ Infrastructure директория не найдена: $InfraDir" -ForegroundColor Red
    exit 1
}

Set-Location $InfraDir

Write-Host "`n=== Логи AI Maturity Platform ===" -ForegroundColor Cyan

if ($Service) {
    Write-Host "Сервис: $Service | Строк: $Tail | Follow: $Follow" -ForegroundColor Yellow
} else {
    Write-Host "Все сервисы | Строк: $Tail | Follow: $Follow" -ForegroundColor Yellow
}

Write-Host "Нажмите Ctrl+C для выхода`n" -ForegroundColor Gray

# Формирование команды
$cmd = @("docker", "compose", "logs")

if ($Service) {
    $cmd += $Service
}

if ($Follow) {
    $cmd += "--follow"
} else {
    $cmd += "--tail=$Tail"
}

# Запуск
& $cmd[0] $cmd[1..($cmd.Length-1)]
