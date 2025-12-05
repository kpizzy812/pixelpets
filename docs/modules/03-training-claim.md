# 03. Training & Claim Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Механика тренировки (24h) и сбора дохода (claim).

---

## Прогресс

### Backend

- [ ] **3.1** Start Training
  - [ ] Эндпоинт `POST /pets/start-training`
  - [ ] Проверка статуса пета (OWNED_IDLE)
  - [ ] Установка training_started_at = now()
  - [ ] Установка training_ends_at = now() + 24h
  - [ ] Статус → TRAINING

- [ ] **3.2** Training Status Check
  - [ ] Логика проверки времени
  - [ ] Автоматический переход TRAINING → READY_TO_CLAIM (при запросе /pets/my)

- [ ] **3.3** Claim Profit
  - [ ] Эндпоинт `POST /pets/claim`
  - [ ] Проверка статуса (READY_TO_CLAIM)
  - [ ] Расчёт профита по формуле
  - [ ] Начисление на баланс
  - [ ] Обновление profit_claimed
  - [ ] Проверка достижения капы → EVOLVED
  - [ ] Иначе → OWNED_IDLE

- [ ] **3.4** Referral Rewards on Claim
  - [ ] Триггер реферальных начислений при claim
  - [ ] Расчёт по 5 уровням
  - [ ] Запись транзакций

- [ ] **3.5** Hall of Fame (Evolved Pets)
  - [ ] Эндпоинт `GET /pets/hall-of-fame`
  - [ ] Список эволвировавших петов пользователя
  - [ ] Статистика: total farmed, lifetime

### Frontend

- [ ] **3.6** Training Timer
  - [ ] Компонент таймера обратного отсчёта
  - [ ] Локальная проверка времени
  - [ ] Автообновление статуса

- [ ] **3.7** Claim Button
  - [ ] Кнопка Claim на карточке
  - [ ] Анимация получения лута
  - [ ] Toast с суммой

- [ ] **3.8** Evolution Animation
  - [ ] Модалка при достижении капы
  - [ ] Показ финальной статистики
  - [ ] Переход в Hall of Fame

### Tests

- [ ] **3.9** Backend tests
  - [ ] Test start training
  - [ ] Test claim calculation
  - [ ] Test cap reached → evolved
  - [ ] Test referral rewards

---

## API Specification

### POST /pets/start-training

**Request:**
```json
{
  "pet_id": 1
}
```

**Response 200:**
```json
{
  "pet_id": 1,
  "status": "TRAINING",
  "training_started_at": "2024-01-01T12:00:00Z",
  "training_ends_at": "2024-01-02T12:00:00Z"
}
```

**Errors:**
- 400: Pet is not in OWNED_IDLE status
- 404: Pet not found

### POST /pets/claim

**Request:**
```json
{
  "pet_id": 1
}
```

**Response 200:**
```json
{
  "profit_claimed": "1.50",
  "new_balance": "151.50",
  "pet_status": "OWNED_IDLE",
  "total_profit_claimed": "25.00",
  "max_profit": "80.00",
  "evolved": false
}
```

**Response 200 (при эволюции):**
```json
{
  "profit_claimed": "1.50",
  "new_balance": "151.50",
  "pet_status": "EVOLVED",
  "total_profit_claimed": "80.00",
  "max_profit": "80.00",
  "evolved": true,
  "hall_of_fame_entry": {
    "pet_name": "Bubble Slime",
    "final_level": "MYTHIC",
    "total_farmed": "80.00",
    "lifetime_days": 45
  }
}
```

### GET /pets/hall-of-fame

**Response 200:**
```json
{
  "pets": [
    {
      "id": 1,
      "pet_type": { "name": "Bubble Slime", "emoji": "🫧" },
      "final_level": "MYTHIC",
      "invested_total": "50.00",
      "total_farmed": "80.00",
      "lifetime_days": 45,
      "evolved_at": "2024-02-15T12:00:00Z"
    }
  ],
  "total_pets_evolved": 3,
  "total_farmed_all_time": "450.00"
}
```

---

## Формулы

### Дневной доход (raw)
```python
daily_profit_raw = invested_total * daily_rate
```

### Фактический доход при claim
```python
max_profit = invested_total * roi_cap_multiplier
remaining_profit = max_profit - profit_claimed
profit_for_claim = min(daily_profit_raw, remaining_profit)
```

### Пример расчёта

```
Pet: Bubble Slime
invested_total: 50 XPET
daily_rate: 1% (0.01)
roi_cap_multiplier: 1.5x

max_profit = 50 * 1.5 = 75 XPET
daily_profit_raw = 50 * 0.01 = 0.5 XPET

Day 1: profit_claimed = 0, claim = 0.5, new profit_claimed = 0.5
Day 50: profit_claimed = 25, claim = 0.5, new profit_claimed = 25.5
...
Day 150: profit_claimed = 74.5, remaining = 0.5, claim = 0.5 → EVOLVED
```

---

## State Machine

```
                      ┌──────────────────┐
                      │                  │
    ┌─────────────────▶   OWNED_IDLE    ◀────────────┐
    │                 │                  │            │
    │                 └────────┬─────────┘            │
    │                          │                      │
    │                   Start Training                │
    │                          │                      │
    │                          ▼                      │
    │                 ┌──────────────────┐            │
    │                 │                  │            │
    │                 │    TRAINING      │            │
    │                 │                  │            │
    │                 └────────┬─────────┘            │
    │                          │                      │
    │                    24h passed                   │
    │                          │                      │
    │                          ▼                      │
    │                 ┌──────────────────┐            │
    │                 │                  │            │
    │                 │ READY_TO_CLAIM   │            │
    │                 │                  │            │
    │                 └────────┬─────────┘            │
    │                          │                      │
    │                       Claim                     │
    │                          │                      │
    │            ┌─────────────┴─────────────┐        │
    │            │                           │        │
    │     cap not reached               cap reached   │
    │            │                           │        │
    │            └───────────────────────────┼────────┘
    │                                        │
    │                                        ▼
    │                              ┌──────────────────┐
    │                              │                  │
    │                              │    EVOLVED       │
    │                              │  (Hall of Fame)  │
    │                              │                  │
    │                              └──────────────────┘
    │
    │  Sell (from any state except EVOLVED)
    │                 ┌──────────────────┐
    └─────────────────│                  │
                      │      SOLD        │
                      │                  │
                      └──────────────────┘
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
