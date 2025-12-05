# 08. Admin Panel Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Административная панель для управления игрой, пользователями, депозитами/выводами.

---

## Прогресс

### Backend (Admin API)

- [ ] **8.1** Admin Auth
  - [ ] Модель AdminUser
  - [ ] Login endpoint
  - [ ] JWT для админов
  - [ ] Role-based access (admin, super_admin)

- [ ] **8.2** Users Management API
  - [ ] `GET /admin/users` - список с фильтрами
  - [ ] `GET /admin/users/:id` - детали пользователя
  - [ ] `POST /admin/users/:id/adjust-balance` - корректировка баланса
  - [ ] `GET /admin/users/:id/transactions` - транзакции пользователя

- [ ] **8.3** Deposits Management API
  - [ ] `GET /admin/deposits` - список заявок
  - [ ] `POST /admin/deposits/:id/approve` - подтвердить
  - [ ] `POST /admin/deposits/:id/reject` - отклонить

- [ ] **8.4** Withdrawals Management API
  - [ ] `GET /admin/withdrawals` - список заявок
  - [ ] `POST /admin/withdrawals/:id/complete` - выполнить
  - [ ] `POST /admin/withdrawals/:id/reject` - отклонить

- [ ] **8.5** Pet Types Management API
  - [ ] `GET /admin/pet-types` - список
  - [ ] `PUT /admin/pet-types/:id` - редактирование
  - [ ] `POST /admin/pet-types` - создание нового

- [ ] **8.6** Tasks Management API
  - [ ] `GET /admin/tasks` - список
  - [ ] `POST /admin/tasks` - создать
  - [ ] `PUT /admin/tasks/:id` - редактировать
  - [ ] `DELETE /admin/tasks/:id` - удалить/скрыть

- [ ] **8.7** Referral Config API
  - [ ] `GET /admin/referral-config`
  - [ ] `PUT /admin/referral-config` - изменить проценты и пороги

- [ ] **8.8** Dashboard Stats API
  - [ ] `GET /admin/stats` - общая статистика
  - [ ] Всего пользователей, активных
  - [ ] Общий баланс в системе
  - [ ] Pending deposits/withdrawals
  - [ ] Daily stats

### Frontend (Admin UI)

- [ ] **8.9** Admin Project Setup
  - [ ] Отдельное Next.js приложение или /admin route
  - [ ] Админ авторизация

- [ ] **8.10** Dashboard Page
  - [ ] Карточки со статистикой
  - [ ] Графики (опционально)
  - [ ] Quick actions

- [ ] **8.11** Users Page
  - [ ] Таблица пользователей
  - [ ] Поиск по telegram_id, ref_code
  - [ ] Детали пользователя
  - [ ] Форма корректировки баланса

- [ ] **8.12** Deposits Page
  - [ ] Таблица заявок
  - [ ] Фильтры по статусу
  - [ ] Кнопки Approve/Reject

- [ ] **8.13** Withdrawals Page
  - [ ] Таблица заявок
  - [ ] Фильтры по статусу
  - [ ] Кнопки Complete/Reject

- [ ] **8.14** Pet Types Page
  - [ ] Список тарифов
  - [ ] Форма редактирования
  - [ ] Добавление нового

- [ ] **8.15** Tasks Page
  - [ ] Список задач
  - [ ] Создание/редактирование
  - [ ] Drag-n-drop для порядка

- [ ] **8.16** Settings Page
  - [ ] Реферальные настройки
  - [ ] Комиссии
  - [ ] Системные параметры

### Tests

- [ ] **8.17** Admin API tests
  - [ ] Auth tests
  - [ ] CRUD operations
  - [ ] Permission tests

---

## API Specification

### POST /admin/auth/login

**Request:**
```json
{
  "username": "admin",
  "password": "secure_password"
}
```

**Response 200:**
```json
{
  "access_token": "jwt_token",
  "admin": {
    "id": 1,
    "username": "admin",
    "role": "super_admin"
  }
}
```

### GET /admin/users

**Query params:**
- `page`, `limit`
- `search` (telegram_id, username, ref_code)
- `sort_by`, `sort_order`

**Response 200:**
```json
{
  "users": [
    {
      "id": 1,
      "telegram_id": 123456789,
      "username": "player1",
      "balance_xpet": "150.50",
      "ref_code": "ABC123",
      "pets_count": 2,
      "total_claimed": "500.00",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1000,
  "page": 1,
  "pages": 50
}
```

### POST /admin/users/:id/adjust-balance

**Request:**
```json
{
  "amount": "50.00",
  "type": "add",
  "reason": "Compensation for bug"
}
```

### GET /admin/deposits

**Query params:**
- `status`: pending, approved, rejected
- `page`, `limit`

**Response 200:**
```json
{
  "deposits": [
    {
      "id": 1,
      "user": { "id": 1, "telegram_id": 123456789, "username": "player1" },
      "amount": "100.00",
      "network": "BEP-20",
      "status": "pending",
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 25,
  "pending_count": 5
}
```

### POST /admin/deposits/:id/approve

**Response 200:**
```json
{
  "success": true,
  "deposit": { ... },
  "user_new_balance": "250.00"
}
```

### GET /admin/stats

**Response 200:**
```json
{
  "users": {
    "total": 10000,
    "active_today": 500,
    "new_today": 50
  },
  "balance": {
    "total_in_system": "500000.00",
    "total_deposited": "600000.00",
    "total_withdrawn": "100000.00"
  },
  "pets": {
    "total_bought": 25000,
    "total_evolved": 5000,
    "total_sold": 2000
  },
  "pending": {
    "deposits": 5,
    "withdrawals": 12
  },
  "today": {
    "deposits_amount": "5000.00",
    "withdrawals_amount": "2000.00",
    "claims_amount": "15000.00",
    "ref_payouts": "3000.00"
  }
}
```

---

## Data Models

```sql
CREATE TYPE admin_role AS ENUM ('admin', 'super_admin');

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role admin_role DEFAULT 'admin',
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Audit log for admin actions
CREATE TABLE admin_audit_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admin_users(id),
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_admin ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_log_action ON admin_audit_log(action);
```

---

## Admin UI Structure

```
/admin
  /layout.tsx (sidebar + header)
  /page.tsx (Dashboard)
  /users
    /page.tsx (Users list)
    /[id]/page.tsx (User details)
  /deposits/page.tsx
  /withdrawals/page.tsx
  /pet-types/page.tsx
  /tasks/page.tsx
  /settings/page.tsx
  /login/page.tsx
```

---

## Dashboard Mockup

```
┌─────────────────────────────────────────────────────────┐
│  Pixel Pets Admin                    [Admin] [Logout]   │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Dashboard│  📊 Dashboard                                │
│ Users    │  ───────────────────────────────────────     │
│ Deposits │                                              │
│ Withdraw │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐        │
│ Pet Types│  │10,000│ │ 500  │ │  5   │ │  12  │        │
│ Tasks    │  │Users │ │Active│ │Dep.  │ │With. │        │
│ Settings │  └──────┘ └──────┘ └──────┘ └──────┘        │
│          │                                              │
│          │  Recent Deposits (Pending)                   │
│          │  ┌─────────────────────────────────────┐     │
│          │  │ #123 | @user1 | 100 XPET | BEP-20  │     │
│          │  │           [Approve] [Reject]        │     │
│          │  └─────────────────────────────────────┘     │
│          │                                              │
│          │  Recent Withdrawals (Pending)                │
│          │  ┌─────────────────────────────────────┐     │
│          │  │ #456 | @user2 | 50 XPET | TON      │     │
│          │  │           [Complete] [Reject]       │     │
│          │  └─────────────────────────────────────┘     │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

---

## Security Considerations

- [ ] Rate limiting на admin endpoints
- [ ] IP whitelist (опционально)
- [ ] 2FA для super_admin (опционально)
- [ ] Audit log для всех действий
- [ ] Secure password hashing (bcrypt)
- [ ] JWT expiration (short-lived)

---

## Заметки

```
(пусто)
```

---

## Блокеры

```
(нет)
```
