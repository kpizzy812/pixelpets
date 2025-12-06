# Frontend Design Backup - 2025-12-07

Этот бэкап содержит полную копию дизайна компонентов и стилей frontend'а перед переделкой оформления.

## Содержимое

- **app/** - все страницы приложения (page.tsx, layout.tsx)
- **components/** - все компоненты UI:
  - `ui/` - базовые UI компоненты (кнопки, прогресс-бары, модалки, и т.д.)
  - `home/` - компоненты главной страницы
  - `shop/` - компоненты магазина питомцев
  - `pet/` - компоненты питомцев
  - `tasks/` - компоненты заданий
  - `referrals/` - компоненты реферальной системы
  - `hall-of-fame/` - компоненты зала славы
  - `wallet/` - компоненты кошелька
  - `spin/` - компоненты рулетки
  - `layout/` - компоненты лейаута (навигация, хедер)
  - `modals/` - модальные окна
  - `providers/` - провайдеры (Telegram, API)
  - `settings/` - компоненты настроек
  - `transactions/` - компоненты транзакций

## Конфигурация

- **globals.css** - глобальные стили
- **next.config.ts** - конфигурация Next.js
- **postcss.config.mjs** - конфигурация PostCSS
- **package.json** - зависимости проекта

## Как восстановить

Если потребуется вернуть старый дизайн:

```bash
# Скопировать компоненты обратно
cp -r frontend-design-backup/2025-12-07/components/* frontend/components/
cp -r frontend-design-backup/2025-12-07/app/* frontend/app/

# Скопировать конфигурацию
cp frontend-design-backup/2025-12-07/globals.css frontend/app/
cp frontend-design-backup/2025-12-07/next.config.ts frontend/
cp frontend-design-backup/2025-12-07/postcss.config.mjs frontend/
```

## Дата создания

7 декабря 2025 года

## Причина бэкапа

Переделка оформления для отличия от дизайна конкурента.
