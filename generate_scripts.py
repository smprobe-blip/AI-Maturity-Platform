# -*- coding: utf-8 -*-
"""
Генератор скриптов для AI Maturity Platform.
Создаёт все .ps1 и .bat файлы с правильной кодировкой UTF-8 BOM.
Запуск: python generate_scripts.py
"""

import os
import sys
from pathlib import Path

# === КОНФИГУРАЦИЯ ===
PROJECT_ROOT = Path(r"C:\Projects\AI-Maturity-Platform")
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
LOG_FILE = SCRIPTS_DIR / "startup.log"

# UTF-8 BOM (Byte Order Mark) - обязателен для Windows PowerShell 5.1
UTF8_BOM = b'\xef\xbb\xbf'


def write_ps1(filepath: Path, content: str) -> None:
    """Запись .ps1 файла с UTF-8 BOM."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(UTF8_BOM)
        f.write(content.encode('utf-8'))
    print(f"  ✅ Создан: {filepath}")


def write_bat(filepath: Path, content: str) -> None:
    """Запись .bat файла с UTF-8 BOM."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(UTF8_BOM)
        f.write(content.encode('utf-8'))
    print(f"  ✅ Создан: {filepath}")


# ============================================================
# 1. START.PS1
# ============================================================
START_PS1 = r'''
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
'''

# ============================================================
# 2. STOP.PS1
# ============================================================
STOP_PS1 = r'''
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
'''

# ============================================================
# 3. STATUS.PS1
# ============================================================
STATUS_PS1 = r'''
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
'''

# ============================================================
# 4. LOGS.PS1
# ============================================================
LOGS_PS1 = r'''
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
'''

# ============================================================
# 5. RESTART.PS1
# ============================================================
RESTART_PS1 = r'''
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
'''

# ============================================================
# BAT-файлы (обёртки для двойного клика)
# ============================================================
def make_bat(ps1_name: str, description: str) -> str:
    return f'''@echo off
chcp 65001 >nul
title {description}
echo.
echo === {description} ===
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0{ps1_name}"
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
'''

BAT_START   = make_bat("start.ps1",   "AI Maturity Platform - Запуск")
BAT_STOP    = make_bat("stop.ps1",    "AI Maturity Platform - Остановка")
BAT_STATUS  = make_bat("status.ps1",  "AI Maturity Platform - Статус")
BAT_LOGS    = make_bat("logs.ps1",    "AI Maturity Platform - Логи")
BAT_RESTART = make_bat("restart.ps1", "AI Maturity Platform - Перезапуск")


# ============================================================
# MAIN
# ============================================================
def main() -> None:
    print("=" * 60)
    print("🚀 Генератор скриптов AI Maturity Platform")
    print("=" * 60)
    print(f"📁 Директория: {SCRIPTS_DIR}")
    print()

    # Создание директории
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Директория готова: {SCRIPTS_DIR}")
    print()

    # Генерация .ps1 файлов
    print("📝 Создание PowerShell скриптов:")
    write_ps1(SCRIPTS_DIR / "start.ps1",    START_PS1.lstrip("\n"))
    write_ps1(SCRIPTS_DIR / "stop.ps1",     STOP_PS1.lstrip("\n"))
    write_ps1(SCRIPTS_DIR / "status.ps1",   STATUS_PS1.lstrip("\n"))
    write_ps1(SCRIPTS_DIR / "logs.ps1",     LOGS_PS1.lstrip("\n"))
    write_ps1(SCRIPTS_DIR / "restart.ps1",  RESTART_PS1.lstrip("\n"))

    print()
    print("📝 Создание BAT-обёрток:")
    write_bat(SCRIPTS_DIR / "start.bat",    BAT_START)
    write_bat(SCRIPTS_DIR / "stop.bat",     BAT_STOP)
    write_bat(SCRIPTS_DIR / "status.bat",   BAT_STATUS)
    write_bat(SCRIPTS_DIR / "logs.bat",     BAT_LOGS)
    write_bat(SCRIPTS_DIR / "restart.bat",  BAT_RESTART)

    print()
    print("=" * 60)
    print("✅ Все скрипты успешно созданы!")
    print("=" * 60)
    print()
    print("🚀 Для запуска выполните:")
    print(f'   cd "{SCRIPTS_DIR}"')
    print(r"   .\start.ps1")
    print()
    print("   Или двойной клик на start.bat")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)