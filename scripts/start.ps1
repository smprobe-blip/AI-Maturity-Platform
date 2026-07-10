#Requires -Version 5.1
<#
.SYNOPSIS
    Запуск AI Maturity Platform.
.DESCRIPTION
    Останавливает старые процессы, клонирует репозиторий (если нужно),
    запускает Docker Compose и проверяет доступность сервисов.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"

# === КОНФИГУРАЦИЯ ===
$ProjectRoot = "C:\Projects\AI-Maturity-Platform"
$InfraDir    = Join-Path $ProjectRoot "infrastructure"
$RepoUrl     = "https://github.com/smprobe-blip/AI-Maturity-Platform.git"
$LogFile     = Join-Path $ProjectRoot "scripts\startup.log"

# === ФУНКЦИИ ===
function Write-Step {
    param([string]$Message, [string]$Color = "Cyan")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$timestamp] $Message"
    Write-Host $Message -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Test-Port {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return ($null -ne $conn)
}

function Stop-ServiceProcess {
    param([string[]]$Names)
    foreach ($name in $Names) {
        Get-Process -Name $name -ErrorAction SilentlyContinue |
            Stop-Process -Force -ErrorAction SilentlyContinue
    }
}

# === ОЧИСТКА ЛОГА ===
New-Item -Path (Split-Path $LogFile) -ItemType Directory -Force | Out-Null
Set-Content -Path $LogFile -Value "=== AI Maturity Platform Startup ===" -Encoding UTF8
Add-Content -Path $LogFile -Value "Start: $(Get-Date)" -Encoding UTF8

# === ШАГ 1: Остановка старых процессов ===
Write-Step "`n=== ШАГ 1: Остановка старых процессов ==="
Write-Step "Остановка Docker контейнеров..."
docker ps -q 2>$null | ForEach-Object { docker stop $_ 2>$null | Out-Null }
docker ps -aq 2>$null | ForEach-Object { docker rm -f $_ 2>$null | Out-Null }

Write-Step "Остановка node/python процессов..."
Stop-ServiceProcess -Names @("node", "python", "python3", "uvicorn")

Write-Step "Очистка dangling Docker образов..."
docker image prune -f 2>$null | Out-Null

# === ШАГ 2: Проверка портов ===
Write-Step "`n=== ШАГ 2: Проверка портов ==="
$ports = @(3000, 8000, 8080, 3001, 9000, 9001, 5432, 8025)
$portsFree = $true

foreach ($port in $ports) {
    if (Test-Port -Port $port) {
        Write-Step "  ❌ Порт $port занят" "Red"
        $portsFree = $false
    } else {
        Write-Step "  ✅ Порт $port свободен" "Green"
    }
}

if (-not $portsFree) {
    Write-Step "`n⚠️  Некоторые порты заняты. Пробую принудительное освобождение..." "Yellow"
    Start-Sleep -Seconds 3
}

# === ШАГ 3: Проверка prerequisites ===
Write-Step "`n=== ШАГ 3: Проверка prerequisites ==="

$prereqs = @{
    "docker"         = "Docker"
    "git"            = "Git"
}

foreach ($cmd in $prereqs.Keys) {
    try {
        $null = Get-Command $cmd -ErrorAction Stop
        $ver = & $cmd --version 2>&1 | Select-Object -First 1
        Write-Step "  ✅ $($prereqs[$cmd]): $ver" "Green"
    } catch {
        Write-Step "  ❌ $($prereqs[$cmd]) не установлен!" "Red"
        if ($cmd -eq "docker") {
            Write-Step "Скачайте: https://www.docker.com/products/docker-desktop" "Yellow"
            exit 1
        }
    }
}

# Проверка docker compose
try {
    $null = docker compose version 2>&1
    Write-Step "  ✅ Docker Compose: плагин установлен" "Green"
} catch {
    try {
        $null = docker-compose version 2>&1
        Write-Step "  ✅ docker-compose: standalone установлен" "Green"
    } catch {
        Write-Step "  ❌ Docker Compose не установлен!" "Red"
        exit 1
    }
}

# === ШАГ 4: Клонирование/обновление репозитория ===
Write-Step "`n=== ШАГ 4: Инициализация проекта ==="

if (-not (Test-Path $ProjectRoot)) {
    New-Item -Path $ProjectRoot -ItemType Directory -Force | Out-Null
    Write-Step "Создана директория: $ProjectRoot"
}

if (-not (Test-Path (Join-Path $ProjectRoot ".git"))) {
    Write-Step "Клонирование репозитория..." "Yellow"
    Set-Location $ProjectRoot
    git clone $RepoUrl .
    if ($LASTEXITCODE -ne 0) {
        Write-Step "❌ Ошибка клонирования!" "Red"
        exit 1
    }
} else {
    Write-Step "Обновление репозитория..."
    Set-Location $ProjectRoot
    git pull --ff-only 2>$null
}

# === ШАГ 5: Запуск Docker Compose ===
Write-Step "`n=== ШАГ 5: Запуск Docker Compose ==="

if (-not (Test-Path $InfraDir)) {
    Write-Step "❌ Директория infrastructure не найдена: $InfraDir" "Red"
    exit 1
}

Set-Location $InfraDir

# Проверка наличия docker-compose.yml
$composeFile = Join-Path $InfraDir "docker-compose.yml"
if (-not (Test-Path $composeFile)) {
    Write-Step "❌ Файл docker-compose.yml не найден!" "Red"
    exit 1
}

Write-Step "Сборка и запуск контейнеров (может занять 5-10 минут)..." "Yellow"
docker compose up -d --build

if ($LASTEXITCODE -ne 0) {
    Write-Step "❌ Ошибка запуска Docker Compose!" "Red"
    Write-Step "Последние логи:" "Yellow"
    docker compose logs --tail=30
    exit 1
}

# === ШАГ 6: Ожидание готовности ===
Write-Step "`n=== ШАГ 6: Ожидание инициализации сервисов ==="
$maxWait = 60
$waited = 0
$backendReady = $false

while ($waited -lt $maxWait -and -not $backendReady) {
    Start-Sleep -Seconds 3
    $waited += 3
    Write-Host "`r  Ожидание: ${waited}/${maxWait} сек..." -NoNewline

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" `
            -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
        }
    } catch {
        # Продолжаем ждать
    }
}

Write-Host ""

# === ШАГ 7: Проверка сервисов ===
Write-Step "`n=== ШАГ 7: Проверка доступности сервисов ==="

$services = @(
    @{ Name = "Frontend";       Url = "http://localhost:3000" },
    @{ Name = "Backend API";    Url = "http://localhost:8000/docs" },
    @{ Name = "Backend Health"; Url = "http://localhost:8000/health" },
    @{ Name = "Keycloak";       Url = "http://localhost:8080" },
    @{ Name = "Baserow";        Url = "http://localhost:3001" },
    @{ Name = "MinIO Console";  Url = "http://localhost:9001" },
    @{ Name = "MailHog UI";     Url = "http://localhost:8025" }
)

$readyCount = 0
foreach ($svc in $services) {
    try {
        $null = Invoke-WebRequest -Uri $svc.Url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Step "  ✅ $($svc.Name): $($svc.Url)" "Green"
        $readyCount++
    } catch {
        Write-Step "  ❌ $($svc.Name): $($svc.Url)" "Red"
    }
}

# === ШАГ 8: Итоговая информация ===
Write-Step "`n=== ШАГ 8: Готово! ===" "Green"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        🚀 AI Maturity Platform запущена!                  ║" -ForegroundColor Green
Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  🔗 Сервисы:                                              ║" -ForegroundColor Green
Write-Host "║     Frontend:       http://localhost:3000                 ║" -ForegroundColor Cyan
Write-Host "║     Backend API:    http://localhost:8000/docs            ║" -ForegroundColor Cyan
Write-Host "║     Keycloak:       http://localhost:8080                 ║" -ForegroundColor Cyan
Write-Host "║     Baserow (CRM):  http://localhost:3001                 ║" -ForegroundColor Cyan
Write-Host "║     MinIO (S3):     http://localhost:9001                 ║" -ForegroundColor Cyan
Write-Host "║     MailHog (SMTP): http://localhost:8025                 ║" -ForegroundColor Cyan
Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  🔑 Креденшиалы:                                          ║" -ForegroundColor Green
Write-Host "║     Keycloak: admin / admin                               ║" -ForegroundColor Yellow
Write-Host "║     Baserow:  admin@baserow.io / baserow                  ║" -ForegroundColor Yellow
Write-Host "║     MinIO:    minioadmin / minioadmin                     ║" -ForegroundColor Yellow
Write-Host "╠════════════════════════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  📊 Статус: $readyCount / $($services.Count) сервисов доступно              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

Write-Step "Завершено: $(Get-Date)"
Write-Step "Сервисов доступно: $readyCount / $($services.Count)"

Write-Host "`n💡 Команды управления:" -ForegroundColor Cyan
Write-Host "   Статус:   .\status.ps1"
Write-Host "   Логи:     .\logs.ps1"
Write-Host "   Остановка: .\stop.ps1"
Write-Host "   Перезапуск: .\restart.ps1"
