# 10. Boosts System Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Система бустов для улучшения питомцев: снэки (одноразовые бонусы), ROI-бусты (постоянное увеличение ROI cap), авто-клейм (подписка).

---

## Типы бустов

### 1. Snacks (Снэки) — Одноразовые бонусы к дневному доходу

Снэки увеличивают доход от следующего клейма:

| Snack | Bonus | Cost Formula | Net Benefit |
|-------|-------|--------------|-------------|
| **Cookie** | +10% | 60% от бонуса | 40% от бонуса |
| **Steak** | +25% | 55% от бонуса | 45% от бонуса |
| **Cake** | +50% | 50% от бонуса | 50% от бонуса |

#### Формула расчёта цены снэка

```python
daily_profit = invested_total * daily_rate
bonus_amount = daily_profit * bonus_percent
cost = bonus_amount * cost_coefficient  # минимум 0.01 XPET
```

#### Пример

```
Pet: Pixel Fox (invested_total: 200 XPET, daily_rate: 1.2%)
Snack: Steak (+25%)

daily_profit = 200 * 0.012 = 2.4 XPET
bonus_amount = 2.4 * 0.25 = 0.6 XPET
cost = 0.6 * 0.55 = 0.33 XPET
net_benefit = 0.6 - 0.33 = 0.27 XPET чистой прибыли
```

#### Правила снэков
- Можно применить только один снэк на пета
- Снэк используется при следующем клейме
- После использования нужно покупать новый

---

### 2. ROI Boost — Постоянное увеличение ROI cap

ROI Boost увеличивает максимальный профит пета (invested_total остаётся прежним):

| Boost | Extra Profit | Cost | Net Benefit |
|-------|--------------|------|-------------|
| +5% | invested × 5% | 25% от extra | 75% от extra |
| +10% | invested × 10% | 25% от extra | 75% от extra |
| +15% | invested × 15% | 25% от extra | 75% от extra |
| +20% | invested × 20% | 25% от extra | 75% от extra |

#### Формула

```python
extra_profit = invested_total * boost_percent
cost = extra_profit * 0.25  # минимум 0.05 XPET
```

#### Важно

- **Бусты НЕ увеличивают invested_total** — увеличивается только ROI cap
- Можно купить несколько бустов, но **максимум +50% суммарно**
- Бусты **постоянные** — действуют до эволюции пета

#### Пример

```
Pet: Glitch Cat (invested_total: 400 XPET, ROI cap: 170%)
Buying: +10% ROI Boost

Без буста:
  max_profit = 400 * 1.70 = 680 XPET

extra_profit = 400 * 0.10 = 40 XPET
cost = 40 * 0.25 = 10 XPET

С бустом:
  new_roi_cap = 170% + 10% = 180%
  max_profit = 400 * 1.80 = 720 XPET

Net benefit = 40 - 10 = 30 XPET дополнительного дохода
```

---

### 3. Auto-Claim — Подписка на автоматический сбор

Автоматически собирает награды с готовых питомцев:

| Feature | Value |
|---------|-------|
| **Стоимость** | 5 XPET/месяц |
| **Комиссия** | 3% с каждого клейма |
| **Периоды** | 1, 3 или 6 месяцев |

#### Как работает

1. Покупаешь подписку (5 XPET × кол-во месяцев)
2. Система автоматически собирает награды с петов в статусе `READY_TO_CLAIM`
3. С каждого авто-клейма удерживается 3% комиссия

#### Пример

```
Подписка: 3 месяца = 15 XPET
Pet claim: 2.4 XPET

commission = 2.4 * 0.03 = 0.072 XPET
player_receives = 2.4 - 0.072 = 2.328 XPET
```

---

## Влияние бустов на пета

### Стоимость пета (invested_total)

**Бусты НЕ изменяют invested_total!**

- Снэки — одноразовый бонус, не меняет ничего
- ROI Boost — увеличивает только roi_cap_multiplier
- Auto-Claim — вообще не связан с конкретным петом

### Что влияет на invested_total

Только:
1. **Покупка пета** — начальная стоимость = base_price
2. **Апгрейд пета** — добавляет разницу между уровнями (без комиссии)

```python
# При покупке
invested_total = base_price

# При апгрейде
upgrade_cost = level_prices[next_level] - invested_total
evolution_fee = upgrade_cost * 0.10  # сжигается
invested_total += upgrade_cost  # fee НЕ добавляется
```

---

## API Specification

### GET /boosts/snacks/{pet_id}

Получить цены всех снэков для пета.

**Response 200:**
```json
{
  "cookie": {
    "cost": "0.03",
    "bonus_percent": 10,
    "bonus_amount": "0.05",
    "net_benefit": "0.02"
  },
  "steak": {
    "cost": "0.066",
    "bonus_percent": 25,
    "bonus_amount": "0.12",
    "net_benefit": "0.054"
  },
  "cake": {
    "cost": "0.12",
    "bonus_percent": 50,
    "bonus_amount": "0.24",
    "net_benefit": "0.12"
  }
}
```

### POST /boosts/snacks/buy

**Request:**
```json
{
  "pet_id": 1,
  "snack_type": "steak"
}
```

**Response 200:**
```json
{
  "snack_id": 123,
  "pet_id": 1,
  "snack_type": "steak",
  "bonus_percent": 25,
  "cost": "0.066",
  "new_balance": "99.934"
}
```

### GET /boosts/roi/{pet_id}

**Response 200:**
```json
{
  "current_boost": 10,
  "max_boost": 50,
  "options": {
    "+5%": {
      "cost": "2.50",
      "boost_percent": 5,
      "extra_profit": "10.00",
      "net_benefit": "7.50",
      "can_buy": true
    },
    "+10%": {
      "cost": "5.00",
      "boost_percent": 10,
      "extra_profit": "20.00",
      "net_benefit": "15.00",
      "can_buy": true
    }
  }
}
```

### POST /boosts/roi/buy

**Request:**
```json
{
  "pet_id": 1,
  "boost_percent": 0.10
}
```

### GET /boosts/auto-claim

**Response 200:**
```json
{
  "is_active": true,
  "expires_at": "2024-03-15T12:00:00Z",
  "days_remaining": 45,
  "total_claims": 128,
  "total_commission": "3.84",
  "commission_percent": 3
}
```

### POST /boosts/auto-claim/buy

**Request:**
```json
{
  "months": 3
}
```

---

## Сводная таблица

| Boost Type | Effect | Cost Model | Duration |
|------------|--------|------------|----------|
| **Snack** | +10/25/50% к клейму | 50-60% от бонуса | 1 клейм |
| **ROI Boost** | +5/10/15/20% к ROI cap | 25% от extra profit | Постоянно |
| **Auto-Claim** | Авто-сбор наград | 5 XPET/мес + 3% | Подписка |

---

## Заметки

- Бусты — это способ увеличить прибыль, но они стоят денег
- Чем дороже пет, тем выгоднее бусты в абсолютных числах
- ROI Boost выгоднее покупать на начальных стадиях пета

---

## Блокеры

```
(нет)
```
