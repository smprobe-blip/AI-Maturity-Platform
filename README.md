# 🤖 AI Maturity Assessment Platform

**B2B-платформа для оценки ИИ-зрелости компаний** с интерактивным калькулятором, Radar Chart визуализацией и отраслевыми бенчмарками.

> **USP:** Диагностика → Финансы → Дорожная карта. Переводим зрелость в рубли (NPV/ROI) за 10-15 минут вместо 3 месяцев консалтинга.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://react.dev/)
[![TypeScript 5](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-24+-blue.svg)](https://www.docker.com/)
[![License MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 💎 Ценностное предложение

### Проблема
- **CAIO/CDO/CIO:** «Пилотный хаос» — ИИ-проекты без измеримого ROI
- **CEO:** Непонятно, сколько вкладывать в ИИ
- **CFO:** Сложно обосновать бюджет на ИИ
- **Интеграторы:** Нет инструмента квалификации лидов

### Решение
**Диагностика за 10-15 минут** по 35 критериям (7 осей × 5 вопросов) с:
- 🎯 **Точностью ±10%** (вместо ±40% у 7-слайдерных аналогов)
- 🧠 **5 паттернами авто-диагностики** (сжатый круг, перекос, звезда с провалами и т.д.)
- 💰 **Финансовым оверлеем** (ROI/NPV в рублях)
- 🏭 **Отраслевым бенчмарком** (контекст «лучше/хуже рынка»)
- 🎯 **Upsell-триггерами** (4 типа: fear_of_loss, bottleneck, new_roles, methodology)

### Уникальное отличие
> Gartner/Deloitte продают **отчёты**. Мы продаём **дорожную карту с денежным выражением** + академическую валидацию (Cronbach's α, EFA).

---
## 🎯 Для кого

| Сегмент | Боль | Как решаем |
|---------|------|------------|
| **CAIO/CDO/CIO** | Непонятно, куда инвестировать | Топ-3 горлышка + Топ-3 якоря |
| **CEO** | Долгий консалтинг | Диагностика за 10-15 минут |
| **CFO** | Нет обоснования бюджета | ROI/NPV в рублях |
| **Интеграторы** | Нет квалификации лидов | Sales-enablement инструмент |
| **Аналитики** | Нет данных для диссертации | DuckDB-выгрузки + Cronbach's α |

---

## ✨ Ключевые возможности

### 🎨 Публичный калькулятор (Entry-калькулятор)
- **35 вопросов** с дескрипторами (7 осей × 5 вопросов)
- **3 варианта отчёта**: Express (бесплатно), Executive (50k ₽), Comprehensive (150k ₽)
- **Radar Chart** с 5 концентрическими зонами зрелости
- **4 слоя данных**: текущее / целевое / бенчмарк / gap
- **Пульсация критичных осей** (≤1.8, 1.5 Гц)
- **5 паттернов диагноза**: compressed_circle, right_skew, left_skew, star_with_gaps, benchmark_parity
- **Upsell-триггеры** с ценами услуг
- **Согласие ПДн** (152-ФЗ)

### 🏢 Административная панель
- **Dashboard** (4 вкладки: Бизнес / Наука / Операции / Качество)
- **Список аудитов** с фильтрами и пагинацией
- **Детальная карточка аудита** (5 вкладок)
- **Export Center** (5-шаговый конфигуратор)
- **Управление пользователями** (RBAC через Keycloak)
- **Audit Trail** (логирование действий)

### 🔬 Аналитика
- **DuckDB** — SQL-запросы к JSON/Parquet без PostgreSQL
- **Cronbach's α** — надёжность осей
- **EFA** — факторный анализ (подтверждение 7-мерной модели)
- **Регрессия** зрелость → ROI
- **Лонгитюд** (раунд 1 vs раунд 2)

---

## 🛠️ Технологический стек

### Backend
| Слой | Технология | Версия |
|------|------------|--------|
| Язык | Python | 3.11+ |
| Фреймворк | FastAPI | 0.110+ |
| Валидация | Pydantic | v2 |
| Аналитика | DuckDB | 0.10+ |
| Логирование | structlog | 24.1+ |
| Тесты | pytest + httpx | 8.0+ |
| Линтеры | Ruff + Black + mypy | — |

### Frontend
| Слой | Технология | Версия |
|------|------------|--------|
| Фреймворк | React + TypeScript | 18 / 5 |
| Сборщик | Vite | 5 |
| Стили | Tailwind CSS | 3.4 |
| Состояние | Zustand | 4.5 |
| Визуализация | D3.js + Recharts | 7.9 / 2.12 |
| Формы | React Hook Form + Zod | 7.51 / 3.22 |
| HTTP | Axios + React Query | 1.6 / 5.28 |
| Тесты | Vitest + RTL | 1.3 |

### Инфраструктура (Россия, 152-ФЗ)
| Слой | Технология |
|------|------------|
| Облако | Yandex Cloud (ru-central1) |
| Хранилище | Yandex Object Storage (S3) |
| Контейнеры | Yandex Managed Kubernetes |
| Auth | Keycloak (self-hosted) |
| CRM | Baserow (self-hosted) |
| SMTP | Yandex 360 / MailHog (dev) |
| Платежи | ЮKassa |
| Мониторинг | Yandex Cloud Monitoring |

---

## 🏗️ Архитектура

### 3.1. Архитектурный стиль
**Модульный монолит** (не микросервисы — избыточно для MVP).

### 3.2. Схема взаимодействия компонентов
[Browser] → [Nginx (YC)] → [React SPA (YC Object Storage + CDN)]
↓
[FastAPI (YC Compute / Kubernetes)]
↓
┌───────────────────────┼───────────────────────┐
↓ ↓ ↓
[Yandex Object Storage] [Keycloak] [Baserow]
(JSON/Parquet/PDF) (Auth + RBAC) (CRM)
↓
[DuckDB embedded]
↓
[Python Analytics (Pandas/SciPy)]


### 3.3. Ключевые модули
| Модуль | Назначение | Технологии |
|--------|------------|------------|
| **Public API** | Entry-калькулятор (лид-магнит) | FastAPI, Pydantic |
| **Admin API** | Back-office для управления | FastAPI, Keycloak RBAC |
| **Storage Service** | Работа с файлами (JSON/Parquet) | Yandex S3, DuckDB |
| **Analytics Service** | Научная аналитика для диссертации | DuckDB, Pandas, SciPy |
| **Integrations** | Baserow, ЮKassa, SMTP | HTTP clients |

### 3.4. Потоки данных
1. Пользователь проходит аудит через Frontend
2. Backend валидирует и рассчитывает индексы (radar_service)
3. JSON сохраняется в Yandex Object Storage (годичная структура)
4. Лид синхронизируется в Baserow через webhook
5. PDF-отчёт генерируется и отправляется email
6. Аналитик запускает DuckDB-запросы для диссертации

## 🚀 Быстрый старт

### Требования
- **Docker Desktop** 24+ ([скачать](https://www.docker.com/products/docker-desktop))
- **Git** ([скачать](https://git-scm.com/))
- **PowerShell** 5.1+ (Windows) или **bash** (Linux/macOS)

### Локальный запуск (5 минут)

#### Windows (PowerShell)
```powershell
# 1. Клонировать репозиторий
git clone https://github.com/smprobe-blip/AI-Maturity-Platform.git
cd AI-Maturity-Platform

# 2. Запустить инфраструктуру
cd infrastructure
docker compose up -d --build

# 3. Подождать 30-40 секунд
Start-Sleep -Seconds 40

# 4. Проверить статус
docker compose ps

Linux/macOS (bash)
# 1. Клонировать репозиторий
git clone https://github.com/smprobe-blip/AI-Maturity-Platform.git
cd AI-Maturity-Platform

# 2. Запустить инфраструктуру
cd infrastructure
docker compose up -d --build

# 3. Подождать 30-40 секунд
sleep 40

# 4. Проверить статус
docker compose ps

Открыть в браузере
Открыть в браузерСервис
URL
Креденшиалы
Frontend
http://localhost:3000
—
Backend API
http://localhost:8000/docs
—
Backend Health
http://localhost:8000/health
—
Keycloak
http://localhost:8080
admin / admin
Baserow (CRM)
http://localhost:3001
admin@baserow.io / baserow
MinIO (S3)
http://localhost:9001
minioadmin / minioadmin
MailHog (SMTP)
http://localhost:8025
—
Остановка проекта
bash
12
Логи в реальном времени
bash
123

## 📁 Структура проекта
AI-Maturity-Platform/
├── backend/ # FastAPI backend
│ ├── app/
│ │ ├── api/v1/
│ │ │ ├── public.py # Public API (калькулятор)
│ │ │ └── admin.py # Admin API (back-office)
│ │ ├── core/
│ │ │ ├── config.py # Настройки (pydantic-settings)
│ │ │ └── auth.py # Keycloak JWT middleware
│ │ ├── models/
│ │ │ └── schemas.py # Pydantic-схемы
│ │ ├── services/
│ │ │ ├── audit_service.py # Бизнес-логика аудитов
│ │ │ ├── radar_service.py # Расчёт индексов
│ │ │ ├── pattern_service.py # 5 паттернов радара
│ │ │ ├── benchmark_service.py # Отраслевые бенчмарки
│ │ │ ├── email_service.py # SMTP отправка
│ │ │ └── lead_service.py # Baserow интеграция
│ │ ├── storage/
│ │ │ ├── json_storage.py # JSON-файлы
│ │ │ └── s3_client.py # Yandex S3
│ │ ├── analytics/
│ │ │ ├── factor_analysis.py # EFA
│ │ │ ├── regression.py # Зрелость → ROI
│ │ │ └── cronbach.py # Надёжность осей
│ │ ── main.py # Точка входа FastAPI
│ ├── tests/ # pytest тесты
│ ├── Dockerfile
│ └── pyproject.toml
│
├── frontend/ # React frontend
│ ├── src/
│ │ ├── components/
│ │ │ ├── ui/ # Дизайн-система (Button, Input...)
│ │ │ ── charts/ # RadarChart, SankeyChart
│ │ ├── pages/
│ │ │ ├── public/ # Page1, Page2, Page3
│ │ │ └── admin/ # Dashboard, Audits, Users...
│ │ ├── store/ # Zustand stores
│ │ ├── services/ # API-клиенты
│ │ ── types/ # TypeScript типы
│ ├── Dockerfile
│ ├── nginx.conf
│ ── package.json
│
├── infrastructure/ # Docker Compose
│ ├── docker-compose.yml
│ └── .env
│
── data_storage/ # Локальное хранилище (dev)
│ ├── raw_audits/2026/ # JSON-файлы аудитов
│ ├── aggregated/ # Parquet-агрегаты
│ ├── reports/ # PDF-отчёты
│ ── logs/ # Audit trail
│
├── docs/ # Документация
│ ├── api.md
│ ├── architecture.md
│ └── deployment.md
│
└── README.md

---

## 📡 API Reference

### Public API (без авторизации)

#### POST `/api/v1/public/audits/express`
Создание экспресс-аудита.

**Request:**
```json
{
  "company_industry": "retail",
  "company_size": "large",
  "contact_email": "ceo@example.com",
  "contact_name": "Ivan Petrov",
  "report_type": "executive",
  "responses": {
    "1": {"1": 4, "2": 3, "3": 5, "4": 2, "5": 4},
    "2": {"1": 3, "2": 4, "3": 2, "4": 3, "5": 3},
    "...": "..."
  },
  "target_scores": {"1": 4.5, "2": 4.0, "...": "..."},
  "pdn_consent": true
}
Response (201 Created):
json
123456789101112131415161718192021222324
GET /api/v1/public/audits/{audit_id}
Получение результатов аудита.
POST /api/v1/public/audits/{audit_id}/email
Отправка отчёта на email.
GET /api/v1/public/benchmarks/{industry}
Отраслевой бенчмарк.
Admin API (требует Keycloak JWT)
Метод
Эндпоинт
Описание
GET
/api/v1/admin/audits
Список аудитов (с фильтрами)
GET
/api/v1/admin/audits/{id}
Детали аудита
GET
/api/v1/admin/dashboard/business
Бизнес-метрики
GET
/api/v1/admin/dashboard/scientific
Научные метрики
GET
/api/v1/admin/leads
Лиды из Baserow
GET
/api/v1/admin/benchmarks
Список бенчмарков
POST
/api/v1/admin/benchmarks/recalculate
Пересчёт бенчмарков
Полная документация: http://localhost:8000/docs (Swagger UI)

## 🔐 Переменные окружения

### Backend (.env)
```env
# Application
APP_NAME=AI Maturity Platform
APP_ENV=development
DEBUG=true
SECRET_KEY=change-me-in-production

# Yandex Object Storage
YANDEX_S3_ENDPOINT=http://minio:9000
YANDEX_S3_ACCESS_KEY=minioadmin
YANDEX_S3_SECRET_KEY=minioadmin
YANDEX_S3_BUCKET=ai-maturity-data
YANDEX_S3_REGION=ru-central1

# Baserow CRM
BASEROW_URL=http://baserow:80
BASEROW_API_TOKEN=your-baserow-token
BASEROW_LEADS_TABLE_ID=511

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=ai-maturity
KEYCLOAK_CLIENT_ID=backend-api
KEYCLOAK_CLIENT_SECRET=your-client-secret

# SMTP
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=test
SMTP_PASSWORD=test

# Data storage
DATA_STORAGE_PATH=/data_storage
RAW_AUDITS_PATH=/data_storage/raw_audits

---

## Шаг 9: Добавление Блока 8 (Переменные окружения)

```powershell
cd C:\Projects\AI-Maturity-Platform

$block8 = @'

## 🔐 Переменные окружения

### Backend (.env)
```env
# Application
APP_NAME=AI Maturity Platform
APP_ENV=development
DEBUG=true
SECRET_KEY=change-me-in-production

# Yandex Object Storage
YANDEX_S3_ENDPOINT=http://minio:9000
YANDEX_S3_ACCESS_KEY=minioadmin
YANDEX_S3_SECRET_KEY=minioadmin
YANDEX_S3_BUCKET=ai-maturity-data
YANDEX_S3_REGION=ru-central1

# Baserow CRM
BASEROW_URL=http://baserow:80
BASEROW_API_TOKEN=your-baserow-token
BASEROW_LEADS_TABLE_ID=511

# Keycloak
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=ai-maturity
KEYCLOAK_CLIENT_ID=backend-api
KEYCLOAK_CLIENT_SECRET=your-client-secret

# SMTP
SMTP_HOST=mailhog
SMTP_PORT=1025
SMTP_USER=test
SMTP_PASSWORD=test

# Data storage
DATA_STORAGE_PATH=/data_storage
RAW_AUDITS_PATH=/data_storage/raw_audits
Frontend (.env)
env
12

## 🧪 Тестирование

### Backend
```bash
cd backend

# Unit-тесты
pytest

# С покрытием
pytest --cov=app --cov-report=html

# Integration-тесты
pytest tests/integration/

# Линтеры
ruff check app/
black --check app/
mypy app/
Frontend
bash
12345678910111213
E2E (Playwright)
bash
123
Требования к покрытию:
Backend: ≥ 80%
Frontend: ≥ 70%
E2E: критические user flows

## 🚢 Деплой на Yandex Cloud

### 1. Создание ресурсов (Terraform)
```bash
cd infrastructure/terraform
terraform init
terraform apply
2. Настройка DNS
Домен: ai-maturity.ru (REG.RU)
A-запись: <IP backend>
CNAME: www → ai-maturity.ru
3. SSL-сертификат
bash
1
4. Деплой через CI/CD
bash
1
5. Проверка
https://ai-maturity.ru
https://ai-maturity.ru/docs (API)
Полная инструкция: docs/deployment.md

## 🛡️ Соответствие 152-ФЗ

| Требование | Реализация |
|------------|------------|
| Хранение ПДн в РФ | Yandex Cloud (ru-central1) |
| Шифрование трафика | TLS 1.3 |
| Шифрование данных | AES-256 (S3 SSE) |
| Анонимизация | 4 уровня (L0–L3) |
| Аудит действий | `/logs/admin_actions.json` |
| 2FA | Keycloak TOTP (Admin/Facilitator) |
| Согласие ПДн | Чекбокс на Page 1 + хранение в JSON |
| NDA | Флаг `nda_signed`, запрет экспорта L0 без NDA |

---

## 🗺️ Roadmap

### ✅ Приоритет 1: Ценностное предложение (реализовано)
- [x] 35 вопросов с дескрипторами
- [x] 5 паттернов радара
- [x] Топ-3 горлышка/якоря
- [x] Upsell-триггеры (4 типа)
- [x] Выбор варианта отчёта (3 типа)
- [x] Согласие ПДн (152-ФЗ)

### 🔄 Приоритет 2: Монетизация (в работе)
- [ ] Финансовый спидометр ROI/NPV
- [ ] Отраслевой бенчмарк (DuckDB)
- [ ] Upsell-воронка (страницы услуг)
- [ ] Экспорт в PDF (3 варианта)

### ️ Приоритет 3: Админка
- [ ] RBAC + Keycloak middleware
- [ ] Детальная карточка аудита (5 вкладок)
- [ ] Export Center (5 шагов)
- [ ] Audit Trail

### 🔬 Приоритет 4: Аналитика
- [ ] Cronbach's α (надёжность осей)
- [ ] EFA (факторный анализ)
- [ ] Регрессия зрелость → ROI
- [ ] Лонгитюд (раунд 1 vs раунд 2)

### 🚀 Приоритет 5: Production
- [ ] Yandex Cloud деплой
- [ ] Мониторинг (YC Monitoring)
- [ ] Бэкапы (ежедневные, 30 дней)
- [ ] Пентест (OWASP Top 10)

---

## 🤝 Вклад в проект

1. **Fork** репозиторий
2. Создайте feature-ветку: `git checkout -b feature/my-feature`
3. Внесите изменения
4. Запустите тесты: `pytest && npm run test`
5. Закоммитьте: `git commit -m "feat: описание"`
6. Запушьте: `git push origin feature/my-feature`
7. Откройте **Pull Request**

**Code Style:**
- Backend: Ruff + Black + mypy (строгая типизация)
- Frontend: ESLint + Prettier + TypeScript strict

---

## 📄 Лицензия

MIT License. См. [LICENSE](LICENSE) для деталей.

---

## 🙏 Благодарности

- Концепция v5.0/v6.0 — академическая основа (РАНХиГС)
- D3.js — визуализация Radar Chart
- FastAPI — быстрый backend
- Tailwind CSS — дизайн-система

---

**Made with ❤️ in Russia** 🇷🇺
