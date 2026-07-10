#Requires -Version 5.1
<#
.SYNOPSIS
Автоматическая пересборка AI Maturity Platform при изменениях файлов.
.DESCRIPTION
Следит за изменениями в backend/ и frontend/ и автоматически пересобирает контейнеры.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

$ProjectRoot = "C:\Projects\AI-Maturity-Platform"
$BackendPath = "$ProjectRoot\backend"
$FrontendPath = "$ProjectRoot\frontend"
$InfraPath = "$ProjectRoot\infrastructure"

Write-Host "`n=== AI Maturity Platform - Watch & Rebuild ===" -ForegroundColor Cyan
Write-Host "Следим за изменениями..." -ForegroundColor Green
Write-Host "Backend: $BackendPath\*.py" -ForegroundColor Gray
Write-Host "Frontend: $FrontendPath\*.{tsx,ts,css}" -ForegroundColor Gray
Write-Host "`nНажмите Ctrl+C для остановки`n" -ForegroundColor Yellow

# Функция для пересборки backend
function Rebuild-Backend {
    Write-Host "`n[BACKEND] Изменения обнаружены. Пересборка..." -ForegroundColor Yellow
    Set-Location $InfraPath
    docker compose up -d --build backend 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[BACKEND] Пересборка завершена" -ForegroundColor Green
    } else {
        Write-Host "[BACKEND] Ошибка пересборки!" -ForegroundColor Red
    }
}

# Функция для пересборки frontend
function Rebuild-Frontend {
    Write-Host "`n[FRONTEND] Изменения обнаружены. Пересборка..." -ForegroundColor Yellow
    Set-Location $InfraPath
    docker compose up -d --build frontend 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[FRONTEND] Пересборка завершена" -ForegroundColor Green
    } else {
        Write-Host "[FRONTEND] Ошибка пересборки!" -ForegroundColor Red
    }
}

# Создаём FileSystemWatcher для backend
$backendWatcher = New-Object System.IO.FileSystemWatcher
$backendWatcher.Path = $BackendPath
$backendWatcher.IncludeSubdirectories = $true
$backendWatcher.EnableRaisingEvents = $true
$backendWatcher.Filter = "*.py"

# Создаём FileSystemWatcher для frontend
$frontendWatcher = New-Object System.IO.FileSystemWatcher
$frontendWatcher.Path = $FrontendPath
$frontendWatcher.IncludeSubdirectories = $true
$frontendWatcher.EnableRaisingEvents = $true
$frontendWatcher.Filter = "*.tsx"

# Регистрируем обработчики событий
$backendAction = Register-ObjectEvent $backendWatcher Changed -Action {
    Rebuild-Backend
}

$frontendAction = Register-ObjectEvent $frontendWatcher Changed -Action {
    Rebuild-Frontend
}

# Бесконечный цикл ожидания
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host "`nWatcher остановлен" -ForegroundColor Yellow
    Unregister-Event $backendAction.Id
    Unregister-Event $frontendAction.Id
}