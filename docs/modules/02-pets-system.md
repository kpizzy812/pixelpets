# 02. Pets System Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Система петов: типы, покупка, апгрейды, уровни, слоты.

---

## Прогресс

### Backend

- [ ] **2.1** Модель PetType
  - [ ] Создать таблицу pet_types
  - [ ] Поля: id, name, emoji, base_price, daily_rate, roi_cap_multiplier, level_prices (JSON)
  - [ ] Seed данные для 5 типов петов

- [ ] **2.2** Модель UserPet
  - [ ] Создать таблицу user_pets
  - [ ] Поля: id, user_id, pet_type_id, invested_total, level, status, slot_index, profit_claimed, training_started_at, training_ends_at, created_at
  - [ ] Enum для status: OWNED_IDLE, TRAINING, READY_TO_CLAIM, EVOLVED, SOLD
  - [ ] Enum для level: BABY, TEEN, ADULT, MYTHIC

- [ ] **2.3** Каталог петов
  - [ ] Эндпоинт `GET /pets/catalog`
  - [ ] Возврат всех типов петов с ценами

- [ ] **2.4** Мои петы
  - [ ] Эндпоинт `GET /pets/my`
  - [ ] Возврат петов пользователя (3 слота)
  - [ ] Включая текущий статус и прогресс

- [ ] **2.5** Покупка пета
  - [ ] Эндпоинт `POST /pets/buy`
  - [ ] Проверка баланса
  - [ ] Проверка свободных слотов (max 3)
  - [ ] Списание XPET
  - [ ] Создание пета на уровне BABY

- [ ] **2.6** Апгрейд пета
  - [ ] Эндпоинт `POST /pets/upgrade`
  - [ ] Проверка баланса
  - [ ] Проверка текущего уровня (не max)
  - [ ] Расчёт стоимости апгрейда
  - [ ] Обновление invested_total и level

- [ ] **2.7** Продажа пета
  - [ ] Эндпоинт `POST /pets/sell`
  - [ ] Возврат 85% от invested_total
  - [ ] Статус → SOLD
  - [ ] Освобождение слота

### Frontend

- [ ] **2.8** Pet Card Component
  - [ ] Отображение аватара, уровня, статуса
  - [ ] Progress bar уровней
  - [ ] Кнопки действий (Start, Claim, Upgrade, Sell)

- [ ] **2.9** Shop Page
  - [ ] Список петов для покупки
  - [ ] Модалка подтверждения покупки
  - [ ] Обработка ошибок (нет слотов, нет баланса)

- [ ] **2.10** Pet Slots on Home
  - [ ] 3 слота с карточками
  - [ ] Пустой слот → CTA "Buy pet"

### Tests

- [ ] **2.11** Backend tests
  - [ ] Test buy pet
  - [ ] Test upgrade pet
  - [ ] Test sell pet
  - [ ] Test slot limits

---

## API Specification

### GET /pets/catalog

**Response 200:**
```json
{
  "pets": [
    {
      "id": 1,
      "name": "Bubble Slime",
      "emoji": "🫧",
      "base_price": "5.00",
      "daily_rate": 0.01,
      "roi_cap_multiplier": 1.5,
      "level_prices": {
        "BABY": "5.00",
        "TEEN": "15.00",
        "ADULT": "30.00",
        "MYTHIC": "50.00"
      }
    }
  ]
}
```

### GET /pets/my

**Response 200:**
```json
{
  "pets": [
    {
      "id": 1,
      "pet_type": { ... },
      "invested_total": "50.00",
      "level": "TEEN",
      "status": "TRAINING",
      "slot_index": 0,
      "profit_claimed": "12.50",
      "max_profit": "80.00",
      "training_ends_at": "2024-01-02T12:00:00Z",
      "upgrade_cost": "15.00",
      "next_level": "ADULT"
    }
  ],
  "free_slots": 2
}
```

### POST /pets/buy

**Request:**
```json
{
  "pet_type_id": 1
}
```

**Response 200:**
```json
{
  "pet": { ... },
  "new_balance": "95.00"
}
```

### POST /pets/upgrade

**Request:**
```json
{
  "pet_id": 1
}
```

### POST /pets/sell

**Request:**
```json
{
  "pet_id": 1
}
```

**Response 200:**
```json
{
  "refund_amount": "42.50",
  "new_balance": "142.50"
}
```

---

## Data Models

```sql
CREATE TABLE pet_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    emoji VARCHAR(10),
    base_price DECIMAL(18, 2) NOT NULL,
    daily_rate DECIMAL(5, 4) NOT NULL,
    roi_cap_multiplier DECIMAL(4, 2) NOT NULL,
    level_prices JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE pet_status AS ENUM ('OWNED_IDLE', 'TRAINING', 'READY_TO_CLAIM', 'EVOLVED', 'SOLD');
CREATE TYPE pet_level AS ENUM ('BABY', 'TEEN', 'ADULT', 'MYTHIC');

CREATE TABLE user_pets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    pet_type_id INTEGER REFERENCES pet_types(id) NOT NULL,
    invested_total DECIMAL(18, 2) NOT NULL,
    level pet_level DEFAULT 'BABY',
    status pet_status DEFAULT 'OWNED_IDLE',
    slot_index INTEGER NOT NULL CHECK (slot_index >= 0 AND slot_index < 3),
    profit_claimed DECIMAL(18, 2) DEFAULT 0,
    training_started_at TIMESTAMP,
    training_ends_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, slot_index)
);

CREATE INDEX idx_user_pets_user_id ON user_pets(user_id);
CREATE INDEX idx_user_pets_status ON user_pets(status);
```

---

## Seed Data

```sql
INSERT INTO pet_types (name, emoji, base_price, daily_rate, roi_cap_multiplier, level_prices) VALUES
('Bubble Slime', '🫧', 5, 0.01, 1.5, '{"BABY": 5, "TEEN": 15, "ADULT": 30, "MYTHIC": 50}'),
('Pixel Fox', '🦊', 50, 0.012, 1.6, '{"BABY": 50, "TEEN": 150, "ADULT": 300, "MYTHIC": 500}'),
('Glitch Cat', '🐱', 100, 0.015, 1.7, '{"BABY": 100, "TEEN": 300, "ADULT": 600, "MYTHIC": 1000}'),
('Robo-Bunny', '🤖', 150, 0.02, 1.8, '{"BABY": 150, "TEEN": 450, "ADULT": 900, "MYTHIC": 1500}'),
('Ember Dragon', '🐉', 300, 0.025, 2.0, '{"BABY": 300, "TEEN": 900, "ADULT": 1800, "MYTHIC": 3000}');
```

---

## Формулы

### Расчёт стоимости апгрейда
```python
upgrade_cost = level_prices[next_level] - invested_total
```

### Максимальный профит
```python
max_profit = invested_total * roi_cap_multiplier
```

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
