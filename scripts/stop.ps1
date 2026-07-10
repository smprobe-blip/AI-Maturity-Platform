#Requires -Version 5.1
<#
.SYNOPSIS
    Остановка AI Maturity Platform.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = "C:\Projects\AI-Maturity-Platform"
$InfraDir    = Join-Path $ProjectRoot "infrastructure"

Write-Host "`n=== Остановка AI Maturity Platform ===" -ForegroundColor Cyan

# Остановка Docker Compose
if (Test-Path $InfraDir) {
    Set-Location $InfraDir
    Write-Host "Остановка контейнеров Docker Compose..." -ForegroundColor Yellow
    docker compose down 2>$null
}

# Принудительная остановка всех контейнеров проекта
Write-Host "Остановка всех контейнеров проекта..." -ForegroundColor Yellow
docker ps -a --filter "label=com.docker.compose.project" -q 2>$null |
    ForEach-Object { docker rm -f $_ 2>$null | Out-Null }

# Остановка локальных процессов
Write-Host "Остановка node/python процессов..." -ForegroundColor Yellow
@("node", "python", "python3", "uvicorn") | ForEach-Object {
    Get-Process -Name $_ -ErrorAction SilentlyContinue |
        Stop-Process -Force -ErrorAction SilentlyContinue
}

# Проверка портов
Write-Host "`n=== Проверка освобождения портов ===" -ForegroundColor Cyan
$ports = @(3000, 8000, 8080, 3001, 9000, 9001, 5432, 8025)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        Write-Host "  ⚠️  Порт $port всё ещё занят" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Порт $port свободен" -ForegroundColor Green
    }
}

Write-Host "`n✅ AI Maturity Platform остановлена" -ForegroundColor Green
