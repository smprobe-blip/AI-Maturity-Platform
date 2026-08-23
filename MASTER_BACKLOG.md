# MASTER BACKLOG — AI Maturity Platform

Обновлено: 2026-08-22

## ✅ Готово (production-ready)

### Ядро продукта
- [x] Исследовательский модуль (v1.9-research-module)
- [x] CSV-экспорт item-level (35 ответов + метаданные)
- [x] UI: премиум-отчёты отключены, бейдж «🔧 В разработке»
- [x] Мини-хедер со ссылкой на netbrainpower.ru

### Инфраструктура
- [x] Production: Timeweb VPS (4 ГБ RAM)
- [x] **Главный лендинг**: netbrainpower.ru (Caddy + статика)
- [x] **Сервис оценки**: audit.netbrainpower.ru (SPA + FastAPI + Postgres)
- [x] HTTPS: Caddy + Let's Encrypt (авто-SSL для обоих доменов)
- [x] CI/CD: push → GitHub Actions → deploy через deployer
- [x] Бэкапы перед деплоем (/opt/backups/deploy/)
- [x] Deploy с --pull=false (обход Docker Hub rate limit)
- [x] **Caddy напрямую проксирует /api на backend** (handle, не handle_path)
- [x] nginx только отдаёт SPA (без проксирования API)

### Безопасность
- [x] SEC-1: SSH hardening (без паролей, fail2ban, современные алгоритмы)
- [x] SSH-доступ с Mac (публичный ключ добавлен в authorized_keys)
- [x] Локальная проверка перед push (scripts/local-check.sh)

### Отслеживание источников
- [x] ?src=direct — прямой заход
- [x] ?src=site — трафик с netbrainpower.ru
- [x] ?src=tg_own — свой Telegram-канал
- [x] ?src=tg_partner_N — партнёрские каналы

## 🔥 Очередь (приоритет)

### EMAIL-1: Отправка отчётов через Yandex Cloud Postbox
**Статус:** диагностика проведена, выбран провайдер  
**Блокер для:** полноценного сбора данных (респонденты не получают PDF-отчёт)

Симптомы:
- POST `/api/v1/public/audits/{id}/email` → 500 Internal Server Error
- POST `/api/v1/public/audits/{id}/service-request` → 500 Internal Server Error
- Лог: `EmailService: send failed: [Errno -3] Temporary failure in name resolution`

Причина: SMTP_HOST=mailhog (дефолт dev-окружения) — в production контейнера нет

План внедрения:
- [ ] Создать API-ключ `yc.postbox.send` в консоли Yandex Cloud
- [ ] Добавить домен `netbrainpower.ru` в Postbox, получить 2 CNAME-записи для DKIM
- [ ] Прописать CNAME в DNS Timeweb, дождаться статуса Verified
- [ ] Создать отправителя `reports@netbrainpower.ru`
- [ ] Добавить в .env на VPS: SMTP_HOST=postbox.cloud.yandex.net, SMTP_PORT=465, SMTP_USER/PASSWORD, SMTP_USE_TLS=true
- [ ] Патч `email_service.py`: поддержка SMTP_SSL (порт 465) + graceful degradation
- [ ] Тест через POST `/api/v1/admin/email/send-test`
- [ ] Проверка доставки на реальный email + отсутствие в спаме

### START: публикация поста в Telegram (после EMAIL-1)
### SEC-2: смена порта SSH 22 → нестандартный
### 6.8: админ-панель лидов (конверсия по источникам)
### Подготовка партнёрских постов (3-5 каналов)

## 📋 Пул задач

- [ ] 6.7-fix: тултипы правее кнопок, ширина ×1.5
- [ ] FE-1: фикс дубля атрибута title в Page2.tsx:231
- [ ] FE-3: code-split фронтенда (bundle 944 KB)
- [ ] 3.4: Keycloak SSO
- [ ] Unit-тесты backend (pytest, цель 80% покрытие)
- [ ] Мониторинг uptime + алерты

## 🎓 Научная программа (магистратура РАНХиГС)

Текущий прогресс: 3 анкеты (1 тест + 2 реальных)
Отраслей: 3 (other, manufacturing, it)
Ролей: 2 (CEO, Specialist)
Уровней: 3 (Начальный, AI-Enabled, AI-Native)

### Ближайшие цели
- [ ] Сбор 30 анкет для пилотного EFA (2 недели)
- [ ] Сбор 150 анкет для финальной валидации (2 месяца)
- [ ] Cronbach's alpha по каждой оси
- [ ] EFA/CFA валидация 7-мерной модели в R
- [ ] Измерительная инвариантность по отраслям
- [ ] Динамические веса осей по отраслям

## 📝 Важные технические заметки

### Проблема 502 Bad Gateway (решено 2026-08-22)
**Симптом:** `curl` через Caddy возвращал 502, но `wget` внутри docker-сети работал.

**Причина:** nginx в frontend-контейнере при старте резолвил `backend` в IP и кэшировал его. При рестарте backend-контейнер получал новый IP, но nginx продолжал стучаться по старому.

**Решение:** Caddy напрямую проксирует `/api` на backend (в Caddyfile `handle /api/*`, **не** `handle_path`, т.к. последний обрезает префикс). Caddy динамически резолвит DNS, не кэшируя IP.

### Docker Hub rate limit (решено 2026-08-22)
**Симптом:** `docker build` падал с `429 Too Many Requests`.

**Решение:** флаг `--pull=false` в `docker compose build` — используем уже скачанные образы.

### Email-отправка (EMAIL-1, в работе)
**Симптом:** 500 при отправке отчёта/заявки, лог: `Temporary failure in name resolution`.

**Причина:** SMTP_HOST=mailhog (dev-дефолт), контейнера mailhog в production нет.

**Решение (запланировано):** Yandex Cloud Postbox (SMTP_SSL на порту 465).
- Данные в РФ (152-ФЗ)
- DKIM/SPF/DMARC из коробки
- Нужны 2 CNAME-записи для верификации домена
