# Pixel Pets - Progress Tracker

Главный файл отслеживания прогресса разработки. Обновляйте статусы после каждой сессии.

**Легенда статусов:**
- [ ] Не начато
- [~] В процессе
- [x] Завершено
- [!] Заблокировано / требует внимания

---

## Общий прогресс

| Модуль | Бэкенд | Фронтенд | Тесты | Статус |
|--------|--------|----------|-------|--------|
| 01. Auth & User | [x] | [ ] | [x] | Backend + тесты готовы |
| 02. Pets System | [x] | [ ] | [x] | Backend + тесты готовы |
| 03. Training & Claim | [x] | [ ] | [x] | Backend + тесты готовы |
| 04. Wallet | [x] | [ ] | [x] | Backend + тесты готовы |
| 05. Referrals | [x] | [ ] | [x] | Backend + тесты готовы |
| 06. Tasks | [x] | [ ] | [x] | Backend + тесты готовы |
| 07. UI & Frontend | n/a | [~] | [ ] | В процессе: Setup, Home, TG SDK |
| 08. Admin Panel | [x] | [ ] | [x] | Backend + тесты готовы |
| 09. Localization | [ ] | [ ] | [ ] | Не начато |

---

## Быстрые ссылки на модули

1. [Auth & User](modules/01-auth-user.md)
2. [Pets System](modules/02-pets-system.md)
3. [Training & Claim](modules/03-training-claim.md)
4. [Wallet](modules/04-wallet.md)
5. [Referrals](modules/05-referrals.md)
6. [Tasks](modules/06-tasks.md)
7. [UI & Frontend](modules/07-ui-frontend.md)
8. [Admin Panel](modules/08-admin-panel.md)
9. [Localization](modules/09-localization.md)

---

## Последние обновления

| Дата | Модуль | Изменение | Автор |
|------|--------|-----------|-------|
| 2025-12-05 | Frontend | Next.js 16 + TG SDK 3.3.9, Home page с carousel, компоненты | Claude |
| 2025-12-05 | Admin Tests | Добавлены тесты админки: 93 теста, всего 243 теста | Claude |
| 2025-12-05 | Tests | Полный набор тестов: 150 тестов, 100% pass rate | Claude |
| 2025-12-05 | Admin Panel | Полная админка: auth, users, deposits, withdrawals, pet_types, tasks, config, stats, logs | Claude |
| 2025-12-05 | Backend | Добавлены Referrals, Tasks модули, Alembic, seed скрипт | Claude |
| 2025-12-05 | Backend | Создана структура проекта, все модели, Auth/Pets/Wallet API | Claude |
| - | - | Инициализация документации | Claude |

---

## Заметки для следующей сессии

_Добавьте здесь важные заметки для продолжения работы:_

```
СЕССИЯ 1 (2025-12-05):
======================

СОЗДАНО:
- backend/app/core/config.py - настройки приложения
- backend/app/core/database.py - подключение PostgreSQL (async)
- backend/app/core/security.py - JWT авторизация (get_current_user)

- backend/app/models/ - все модели:
  - enums.py - PetStatus, PetLevel, TxType, NetworkType и др.
  - user.py - User модель
  - pet.py - PetType, UserPet модели
  - transaction.py - Transaction, DepositRequest, WithdrawRequest
  - task.py - Task, UserTask модели
  - referral.py - ReferralStats, ReferralReward модели

- backend/app/schemas/ - Pydantic схемы:
  - user.py - UserResponse, AuthResponse, TelegramAuthRequest
  - pet.py - PetCatalogResponse, UserPetResponse, ClaimResponse и др.
  - wallet.py - WalletResponse, DepositRequestResponse и др.

- backend/app/services/ - бизнес-логика:
  - auth.py - validate_telegram_init_data, create_access_token, get_or_create_user
  - pets.py - buy_pet, upgrade_pet, sell_pet, start_training, claim_profit
  - wallet.py - create_deposit_request, create_withdraw_request, get_transactions

- backend/app/api/routes/ - API роуты:
  - auth.py - POST /auth/telegram, GET /auth/me
  - pets.py - GET /pets/catalog, GET /pets/my, POST /pets/buy, /upgrade, /sell, /start-training, /claim
  - wallet.py - GET /wallet, POST /wallet/deposit-request, /withdraw-request, GET /wallet/transactions

СЛЕДУЮЩИЕ ШАГИ:
1. Создать referrals service и router ✅
2. Создать tasks service и router ✅
3. Настроить Alembic ✅
4. Создать seed данные для pet_types ✅
5. Начать frontend (Next.js + Telegram SDK)

---

СЕССИЯ 2 (продолжение 2025-12-05):
==================================

ДОБАВЛЕНО:
- backend/app/schemas/referral.py - RefLinkResponse, ReferralsResponse
- backend/app/services/referrals.py - process_referral_rewards, get_referral_stats
- backend/app/api/routes/referrals.py - GET /referrals/link, GET /referrals

- backend/app/schemas/task.py - TasksListResponse, TaskCheckResponse
- backend/app/services/tasks.py - get_tasks_for_user, check_task
- backend/app/api/routes/tasks.py - GET /tasks, POST /tasks/check

- backend/alembic/ - настроен Alembic для миграций
- backend/app/scripts/seed.py - seed данные для pet_types и tasks

ИНТЕГРАЦИЯ:
- Реферальные награды теперь начисляются при каждом claim_profit

ВСЕ API ENDPOINTS BACKEND ГОТОВЫ:
- POST /auth/telegram, GET /auth/me
- GET /pets/catalog, GET /pets/my, POST /pets/buy, /upgrade, /sell, /start-training, /claim
- GET /pets/hall-of-fame
- GET /wallet, POST /wallet/deposit-request, /withdraw-request, GET /wallet/transactions
- GET /referrals/link, GET /referrals
- GET /tasks, POST /tasks/check

СЛЕДУЮЩИЕ ШАГИ:
1. Создать .env файл и настроить PostgreSQL
2. Запустить: alembic revision --autogenerate -m "initial"
3. Применить: alembic upgrade head
4. Запустить seed: python -m app.scripts.seed
5. Начать frontend (Next.js + Telegram SDK)

---

СЕССИЯ 3 (продолжение 2025-12-05):
==================================

ДОБАВЛЕНА ПОЛНАЯ АДМИНКА:

Модели:
- backend/app/models/admin.py - Admin (username, password_hash, role, is_active)
- backend/app/models/config.py - SystemConfig (key-value store для настроек)
- backend/app/models/admin_log.py - AdminActionLog (аудит действий)
- backend/app/models/enums.py - добавлен AdminRole (SUPER_ADMIN, ADMIN, MODERATOR)

Схемы:
- backend/app/schemas/admin.py - все DTO для админки

Сервисы (модульная структура):
- backend/app/services/admin/__init__.py
- backend/app/services/admin/auth.py - authenticate_admin, create_admin, hash/verify password
- backend/app/services/admin/users.py - get_users_list, get_user_detail, adjust_user_balance
- backend/app/services/admin/deposits.py - get_deposits_list, approve/reject_deposit
- backend/app/services/admin/withdrawals.py - get_withdrawals_list, complete/reject_withdrawal
- backend/app/services/admin/pet_types.py - CRUD для pet types
- backend/app/services/admin/tasks.py - CRUD для tasks
- backend/app/services/admin/config.py - get/set config, referral config, default values
- backend/app/services/admin/stats.py - get_dashboard_stats
- backend/app/services/admin/logs.py - log_admin_action, get_admin_logs

Роуты (модульная структура):
- backend/app/api/routes/admin/__init__.py
- backend/app/api/routes/admin/auth.py - POST /admin/login, GET /admin/me, POST /admin/admins
- backend/app/api/routes/admin/users.py - GET /admin/users, GET /admin/users/{id}, POST /admin/users/{id}/balance
- backend/app/api/routes/admin/deposits.py - GET /admin/deposits, POST /admin/deposits/{id}/action
- backend/app/api/routes/admin/withdrawals.py - GET /admin/withdrawals, POST /admin/withdrawals/{id}/action
- backend/app/api/routes/admin/pet_types.py - CRUD /admin/pet-types
- backend/app/api/routes/admin/tasks.py - CRUD /admin/tasks
- backend/app/api/routes/admin/config.py - GET/PUT /admin/config, /admin/config/referrals
- backend/app/api/routes/admin/stats.py - GET /admin/stats/dashboard
- backend/app/api/routes/admin/logs.py - GET /admin/logs

Security:
- backend/app/core/admin_security.py - create_admin_access_token, get_current_admin, require_role

Seed обновлен:
- Создает super admin (admin/admin123) при первом запуске
- Создает default system config

РОЛИ АДМИНОВ:
- SUPER_ADMIN: полный доступ, управление другими админами, изменение конфигов
- ADMIN: управление пользователями, депозитами, выводами, pet types, tasks
- MODERATOR: только просмотр

ADMIN API ENDPOINTS:
- POST /admin/login - авторизация
- GET /admin/me - текущий профиль
- POST /admin/admins - создать админа (super_admin only)
- PATCH /admin/admins/{id} - обновить админа (super_admin only)
- GET /admin/users - список пользователей с поиском и пагинацией
- GET /admin/users/{id} - детали пользователя со статистикой
- POST /admin/users/{id}/balance - корректировка баланса
- GET /admin/deposits - список депозитов
- POST /admin/deposits/{id}/action - approve/reject депозит
- GET /admin/withdrawals - список выводов
- POST /admin/withdrawals/{id}/action - complete/reject вывод
- GET /admin/pet-types - список pet types
- POST /admin/pet-types - создать
- PATCH /admin/pet-types/{id} - обновить
- DELETE /admin/pet-types/{id} - удалить (soft)
- GET /admin/tasks - список tasks
- POST /admin/tasks - создать
- PATCH /admin/tasks/{id} - обновить
- DELETE /admin/tasks/{id} - удалить (soft)
- GET /admin/config - все настройки
- PUT /admin/config/{key} - обновить настройку
- GET /admin/config/referrals - настройки рефералки
- PUT /admin/config/referrals - обновить настройки рефералки
- GET /admin/stats/dashboard - статистика для дашборда
- GET /admin/logs - логи действий админов

СЛЕДУЮЩИЕ ШАГИ:
1. Создать alembic migration с новыми таблицами
2. Начать frontend (Next.js + Telegram SDK)
3. Создать админ-панель UI (можно на React/Next.js отдельно)

---

СЕССИЯ 4 (продолжение 2025-12-05):
==================================

ДОБАВЛЕНЫ ПОЛНЫЕ ТЕСТЫ BACKEND:

Инфраструктура:
- backend/tests/__init__.py - пакет тестов
- backend/tests/conftest.py - фикстуры, тестовая БД SQLite in-memory
- backend/pytest.ini - конфигурация pytest

Тестовые файлы:
- backend/tests/test_auth.py - 23 теста
  - генерация ref_code
  - валидация Telegram initData
  - создание/декодирование JWT
  - создание/обновление пользователей
  - API endpoints /auth/telegram, /auth/me

- backend/tests/test_pets.py - 47 тестов
  - расчёт уровней, прибыли, стоимости апгрейда
  - покупка питомца (успех, недостаточно баланса, нет слотов)
  - апгрейд (успех, max level, sold/evolved)
  - продажа (85% refund, нельзя продать evolved)
  - тренировка (start, check status)
  - клейм прибыли (расчёт, эволюция при ROI cap)
  - Hall of Fame
  - все API endpoints /pets/*

- backend/tests/test_wallet.py - 35 тестов
  - расчёт комиссии вывода ($1 + 2%)
  - wallet info с pending requests
  - создание депозитов (BEP20, Solana, TON)
  - создание выводов (минимум $5, проверка баланса)
  - история транзакций (пагинация, фильтр по типу)
  - все API endpoints /wallet/*

- backend/tests/test_referrals.py - 28 тестов
  - подсчёт активных рефералов (только с питомцами)
  - разблокировка уровней (1-5)
  - получение цепочки рефереров (до 5 уровней)
  - распределение наград (20%, 15%, 10%, 5%, 2%)
  - создание ReferralReward и Transaction записей
  - статистика рефералов
  - все API endpoints /referrals/*

- backend/tests/test_tasks.py - 17 тестов
  - получение списка задач с статусом выполнения
  - выполнение задачи (награда, транзакция)
  - нельзя выполнить дважды
  - неактивные задачи не показываются
  - все API endpoints /tasks/*

ИСПРАВЛЕННЫЕ БАГИ В КОДЕ:
- app/services/pets.py:284 - check_training_status был async но не использовал await
- app/services/pets.py:312 - вызов без await
- app/services/referrals.py:180 - getattr возвращал None вместо Decimal("0")

РЕЗУЛЬТАТЫ:
- 150 тестов написано
- 150 тестов проходят (100% pass rate)
- Время выполнения: ~6.6 секунд

ЗАПУСК ТЕСТОВ:
cd backend
source venv/bin/activate
python -m pytest tests/ -v

СЛЕДУЮЩИЕ ШАГИ:
1. Добавить тесты для Admin Panel
2. Начать frontend (Next.js + Telegram SDK)
3. Создать админ-панель UI
```

---

## Зависимости между модулями

```
01-auth-user
    └── 02-pets-system
          ├── 03-training-claim
          │     └── 05-referrals (claim triggers ref rewards)
          └── 04-wallet
    └── 05-referrals
    └── 06-tasks
    └── 08-admin-panel

07-ui-frontend (зависит от всех API)
09-localization (применяется ко всему UI)
```

**Рекомендуемый порядок разработки:**
1. Auth & User (база)
2. Pets System (ядро игры)
3. Training & Claim (основная механика)
4. Wallet (экономика)
5. Referrals (монетизация)
6. Tasks (вовлечение)
7. Admin Panel (управление)
8. UI & Frontend (интерфейс)
9. Localization (масштабирование)
