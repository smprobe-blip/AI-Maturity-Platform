#Requires -Version 5.1
<#
.SYNOPSIS
    Проверка статуса AI Maturity Platform.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ProjectRoot = "C:\Projects\AI-Maturity-Platform"
$InfraDir    = Join-Path $ProjectRoot "infrastructure"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       📊 Статус AI Maturity Platform                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

# Docker контейнеры
Write-Host "`n=== Docker контейнеры ===" -ForegroundColor Yellow
if (Test-Path $InfraDir) {
    Set-Location $InfraDir
    docker compose ps
} else {
    Write-Host "❌ Infrastructure директория не найдена" -ForegroundColor Red
}

# Проверка сервисов
Write-Host "`n=== Доступность сервисов ===" -ForegroundColor Yellow
$services = @(
    @{ Name = "Frontend";       Url = "http://localhost:3000" },
    @{ Name = "Backend API";    Url = "http://localhost:8000/docs" },
    @{ Name = "Backend Health"; Url = "http://localhost:8000/health" },
    @{ Name = "Keycloak";       Url = "http://localhost:8080" },
    @{ Name = "Baserow";        Url = "http://localhost:3001" },
    @{ Name = "MinIO Console";  Url = "http://localhost:9001" },
    @{ Name = "MailHog UI";     Url = "http://localhost:8025" }
)

foreach ($svc in $services) {
    try {
        $null = Invoke-WebRequest -Uri $svc.Url -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✅ $($svc.Name): $($svc.Url)" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $($svc.Name): $($svc.Url)" -ForegroundColor Red
    }
}

# Использование ресурсов
Write-Host "`n=== Использование ресурсов Docker ===" -ForegroundColor Yellow
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>$null
