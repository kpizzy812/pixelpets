# 02. Pets System Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Система петов: типы, покупка, апгрейды, уровни, слоты, продажа с динамической комиссией.

---

## Pet Types (Типы питомцев)

В игре 6 типов питомцев с разными характеристиками:

| Pet | Emoji | Base Price | Daily Rate | ROI Cap | Levels (BABY → ADULT → MYTHIC) |
|-----|-------|------------|------------|---------|-------------------------------|
| **Bubble Slime** | 🫧 | 5 XPET | 1.0% | 150% | 5 → 20 → 50 |
| **Pixel Fox** | 🦊 | 50 XPET | 1.2% | 160% | 50 → 200 → 500 |
| **Glitch Cat** | 🐱 | 100 XPET | 1.5% | 170% | 100 → 400 → 1000 |
| **Robo-Bunny** | 🤖 | 250 XPET | 2.0% | 180% | 250 → 1000 → 2500 |
| **Crystal Turtle** | 🐢 | 500 XPET | 2.2% | 190% | 500 → 2000 → 5000 |
| **Ember Dragon** | 🐉 | 1000 XPET | 2.5% | 200% | 1000 → 4000 → 10000 |

### Расшифровка:
- **Base Price** — стоимость покупки пета (BABY level)
- **Daily Rate** — дневной доход в % от invested_total
- **ROI Cap** — максимальный профит (% от invested_total), после достижения пет эволюционирует
- **Levels** — стоимость пета на каждом уровне (BABY → ADULT → MYTHIC)

### Уровни питомцев

В игре 3 уровня: **BABY** → **ADULT** → **MYTHIC**

---

## Апгрейд питомца

### Формула стоимости апгрейда

```python
upgrade_cost = level_prices[next_level] - invested_total
```

### Комиссия за эволюцию: 10%

При апгрейде пета взимается **10% комиссия** от стоимости апгрейда:

```python
evolution_fee = upgrade_cost * 0.10
total_cost = upgrade_cost + evolution_fee
```

**Важно:** Комиссия сжигается и НЕ добавляется к invested_total пета.

### Пример расчёта апгрейда

```
Pet: Bubble Slime (Level: BABY, invested_total: 5 XPET)
Target level: ADULT (level_price: 20 XPET)

upgrade_cost = 20 - 5 = 15 XPET
evolution_fee = 15 * 0.10 = 1.5 XPET
total_cost = 15 + 1.5 = 16.5 XPET

После апгрейда:
- invested_total = 5 + 15 = 20 XPET (fee не добавляется)
- Level = ADULT
```

---

## Продажа питомца (Early Sell)

### Динамическая комиссия

Комиссия за досрочную продажу зависит от прогресса получения профита:

| Profit Progress | Fee | Refund |
|-----------------|-----|--------|
| 0% (только купил) | 15% | 85% |
| 25% ROI | ~36% | ~64% |
| 50% ROI | ~58% | ~42% |
| 75% ROI | ~79% | ~21% |
| 100% ROI (cap) | 100% | 0% |

### Формула

```python
SELL_BASE_FEE = 0.15   # 15% минимальная комиссия
SELL_MAX_FEE = 1.0     # 100% максимальная комиссия

profit_ratio = profit_claimed / max_profit
fee = 0.15 + (profit_ratio * 0.85)
refund = invested_total * (1 - fee)
```

### Логика

Чем больше профита уже получено с пета, тем выше комиссия:
- **Только купил** (0% profit): комиссия 15%, возврат 85%
- **Достиг ROI cap** (100% profit): комиссия 100%, возврат 0%

Линейная интерполяция между 15% и 100%.

### Пример

```
Pet: Pixel Fox
invested_total: 200 XPET
profit_claimed: 80 XPET
max_profit: 200 * 1.6 = 320 XPET

profit_ratio = 80 / 320 = 0.25 (25%)
fee = 0.15 + (0.25 * 0.85) = 0.3625 (36.25%)
refund = 200 * (1 - 0.3625) = 127.5 XPET
```

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
      "image_key": "bubble",
      "base_price": "5.00",
      "daily_rate": 0.01,
      "roi_cap_multiplier": 1.5,
      "level_prices": {
        "BABY": 5,
        "ADULT": 20,
        "MYTHIC": 50
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
INSERT INTO pet_types (name, emoji, image_key, base_price, daily_rate, roi_cap_multiplier, level_prices) VALUES
('Bubble Slime', '🫧', 'bubble', 5, 0.01, 1.5, '{"BABY": 5, "ADULT": 20, "MYTHIC": 50}'),
('Pixel Fox', '🦊', 'fox', 50, 0.012, 1.6, '{"BABY": 50, "ADULT": 200, "MYTHIC": 500}'),
('Glitch Cat', '🐱', 'cat', 100, 0.015, 1.7, '{"BABY": 100, "ADULT": 400, "MYTHIC": 1000}'),
('Robo-Bunny', '🤖', 'rabbit', 250, 0.02, 1.8, '{"BABY": 250, "ADULT": 1000, "MYTHIC": 2500}'),
('Crystal Turtle', '🐢', 'turtle', 500, 0.022, 1.9, '{"BABY": 500, "ADULT": 2000, "MYTHIC": 5000}'),
('Ember Dragon', '🐉', 'dragon', 1000, 0.025, 2.0, '{"BABY": 1000, "ADULT": 4000, "MYTHIC": 10000}');
```

---

## Формулы

### Расчёт стоимости апгрейда
```python
upgrade_cost = level_prices[next_level] - invested_total
evolution_fee = upgrade_cost * 0.10  # 10% комиссия
total_cost = upgrade_cost + evolution_fee
```

### Максимальный профит
```python
max_profit = invested_total * roi_cap_multiplier
```

### Продажа с динамической комиссией
```python
profit_ratio = profit_claimed / max_profit
fee = 0.15 + (profit_ratio * 0.85)  # от 15% до 100%
refund = invested_total * (1 - fee)
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
