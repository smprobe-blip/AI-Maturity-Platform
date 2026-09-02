# Партнёрская атрибуция (src-теги)

Любая ссылка вида `https://netbrainpower.ru/?src=<тег>` автоматически пробрасывает тег
в кнопки аудиторку: посетитель уходит на `https://audit.netbrainpower.ru/?src=<тег>`,
и источник сохраняется в аудите. Регистрация тега в коде не нужна — работает любой тег
по маске `[a-z0-9_-]`, до 64 символов. Нижеследующий реестр — справочник для аналитики.

## Правило именования
`<канал>_<номер>_<имя>` — например `tg_partner_1_ai_community`.
Каналы: `tg` (Telegram), `vc` (VC.ru), `habr`, `vk`, `email`, `personal` (личные рассылки), `site` (сам лендинг, по умолчанию).

## Активные теги
| Тег | Канал / партнёр | Ссылка для публикации |
|---|---|---|
| `personal` | Личные рассылки автора | `https://netbrainpower.ru/?src=personal` |
| `tg_partner_1_ai_community` | Telegram «AI Community» | `https://netbrainpower.ru/?src=tg_partner_1_ai_community` |
| `tg_partner_2_retail_ru` | Ритейл-сообщество | `https://netbrainpower.ru/?src=tg_partner_2_retail_ru` |
| `tg_partner_3_ceo_club` | Клуб топ-менеджеров | `https://netbrainpower.ru/?src=tg_partner_3_ceo_club` |
| `tg_partner_4_habr` | Habr | `https://netbrainpower.ru/?src=tg_partner_4_habr` |
| `site` | Органический трафик лендинга (по умолчанию) | `https://netbrainpower.ru` |

## Статистика
```
python3 scripts/partner_stats.py                 # таблица по всем источникам
python3 scripts/partner_stats.py --json          # машиночитаемый вывод
python3 scripts/partner_stats.py --path /opt/ai-maturity-platform/data_storage
```
Источник берётся из поля `request.source` аудита (отсутствие = `unknown`).
