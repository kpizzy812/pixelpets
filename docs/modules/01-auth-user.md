# 01. Auth & User Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Модуль авторизации через Telegram и управления пользователями.

---

## Прогресс

### Backend

- [ ] **1.1** Модель User в БД
  - [ ] Создать таблицу users
  - [ ] Поля: id, telegram_id, username, balance_xpet, ref_code, referrer_id, ref_levels_unlocked, created_at
  - [ ] Индексы: telegram_id (unique), ref_code (unique)

- [ ] **1.2** Telegram Auth
  - [ ] Эндпоинт `POST /auth/telegram`
  - [ ] Валидация initData (hash проверка)
  - [ ] Создание/обновление пользователя
  - [ ] Генерация JWT токена
  - [ ] Обработка реферального кода при регистрации

- [ ] **1.3** User Profile
  - [ ] Эндпоинт `GET /me`
  - [ ] Возврат: профиль, баланс, реф-код, статистика

### Frontend

- [ ] **1.4** Auth Flow
  - [ ] Интеграция Telegram Mini App SDK
  - [ ] Получение initData
  - [ ] Отправка на бэкенд
  - [ ] Сохранение токена

- [ ] **1.5** Auth Context
  - [ ] React Context для авторизации
  - [ ] Хранение user data
  - [ ] Auto-refresh токена

### Tests

- [ ] **1.6** Backend tests
  - [ ] Test initData validation
  - [ ] Test user creation
  - [ ] Test referral link processing

---

## API Specification

### POST /auth/telegram

**Request:**
```json
{
  "init_data": "query_string_from_telegram",
  "ref_code": "optional_referrer_code"
}
```

**Response 200:**
```json
{
  "access_token": "jwt_token",
  "user": {
    "id": 1,
    "telegram_id": 123456789,
    "username": "player1",
    "balance_xpet": "0.00",
    "ref_code": "ABC123",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### GET /me

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": 1,
  "telegram_id": 123456789,
  "username": "player1",
  "balance_xpet": "150.50",
  "ref_code": "ABC123",
  "referrer_id": null,
  "ref_levels_unlocked": 1,
  "stats": {
    "total_pets_owned": 3,
    "total_claimed": "500.00",
    "total_ref_earned": "45.00"
  }
}
```

---

## Data Model

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10) DEFAULT 'en',
    balance_xpet DECIMAL(18, 2) DEFAULT 0,
    ref_code VARCHAR(10) UNIQUE NOT NULL,
    referrer_id INTEGER REFERENCES users(id),
    ref_levels_unlocked INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_ref_code ON users(ref_code);
CREATE INDEX idx_users_referrer_id ON users(referrer_id);
```

---

## Заметки

_Добавьте заметки по ходу разработки:_

```
(пусто)
```

---

## Блокеры

_Если что-то блокирует работу:_

```
(нет)
```
