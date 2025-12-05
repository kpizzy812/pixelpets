# 05. Referrals Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

5-уровневая реферальная система с начислением % от claim партнёров.

---

## Прогресс

### Backend

- [ ] **5.1** Модель ReferralStats
  - [ ] Таблица referral_stats или поля в users
  - [ ] Счётчики по уровням: level_1_count, level_2_count, etc.
  - [ ] total_ref_earned_xpet

- [ ] **5.2** Referral Link
  - [ ] Эндпоинт `GET /referrals/link`
  - [ ] Генерация deep link для Telegram

- [ ] **5.3** Referral Stats
  - [ ] Эндпоинт `GET /referrals`
  - [ ] Структура рефералов по уровням
  - [ ] Общий заработок
  - [ ] Прогресс открытия уровней

- [ ] **5.4** Referral Tree
  - [ ] Функция получения цепочки реферреров (до 5 уровней вверх)
  - [ ] Кэширование или оптимизация запросов

- [ ] **5.5** Referral Reward Calculation
  - [ ] При каждом claim
  - [ ] Расчёт по формуле для каждого уровня
  - [ ] Проверка открытия уровня у получателя
  - [ ] Начисление на баланс

- [ ] **5.6** Level Unlock Logic
  - [ ] Подсчёт активных рефералов (купили хотя бы 1 пета)
  - [ ] Автообновление ref_levels_unlocked

### Frontend

- [ ] **5.7** Referrals Screen
  - [ ] Реф-ссылка с кнопкой Copy/Share
  - [ ] Статистика заработка
  - [ ] Количество рефералов

- [ ] **5.8** Level Progress UI
  - [ ] 5 уровней с прогрессом открытия
  - [ ] Замочки на закрытых уровнях
  - [ ] Проценты и условия

### Tests

- [ ] **5.9** Backend tests
  - [ ] Test referral chain
  - [ ] Test reward distribution
  - [ ] Test level unlock

---

## API Specification

### GET /referrals/link

**Response 200:**
```json
{
  "ref_code": "ABC123",
  "ref_link": "https://t.me/pixelpets_bot?start=ABC123",
  "share_text": "Join Pixel Pets and earn XPET! 🐾"
}
```

### GET /referrals

**Response 200:**
```json
{
  "ref_code": "ABC123",
  "total_earned_xpet": "125.50",
  "levels_unlocked": 3,
  "levels": [
    {
      "level": 1,
      "percent": 20,
      "unlocked": true,
      "referrals_count": 5,
      "earned_xpet": "80.00"
    },
    {
      "level": 2,
      "percent": 15,
      "unlocked": true,
      "unlock_requirement": 3,
      "referrals_count": 12,
      "earned_xpet": "35.00"
    },
    {
      "level": 3,
      "percent": 10,
      "unlocked": true,
      "unlock_requirement": 5,
      "referrals_count": 8,
      "earned_xpet": "10.50"
    },
    {
      "level": 4,
      "percent": 5,
      "unlocked": false,
      "unlock_requirement": 10,
      "referrals_count": 0,
      "earned_xpet": "0.00",
      "progress": "5/10 active"
    },
    {
      "level": 5,
      "percent": 2,
      "unlocked": false,
      "unlock_requirement": 20,
      "referrals_count": 0,
      "earned_xpet": "0.00",
      "progress": "5/20 active"
    }
  ],
  "active_referrals_count": 5
}
```

---

## Data Model

```sql
-- Расширение таблицы users или отдельная таблица
CREATE TABLE referral_stats (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    level_1_count INTEGER DEFAULT 0,
    level_2_count INTEGER DEFAULT 0,
    level_3_count INTEGER DEFAULT 0,
    level_4_count INTEGER DEFAULT 0,
    level_5_count INTEGER DEFAULT 0,
    level_1_earned DECIMAL(18, 2) DEFAULT 0,
    level_2_earned DECIMAL(18, 2) DEFAULT 0,
    level_3_earned DECIMAL(18, 2) DEFAULT 0,
    level_4_earned DECIMAL(18, 2) DEFAULT 0,
    level_5_earned DECIMAL(18, 2) DEFAULT 0,
    total_earned DECIMAL(18, 2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Для отслеживания реферальных начислений
CREATE TABLE referral_rewards (
    id SERIAL PRIMARY KEY,
    from_user_id INTEGER REFERENCES users(id) NOT NULL,
    to_user_id INTEGER REFERENCES users(id) NOT NULL,
    level INTEGER NOT NULL CHECK (level >= 1 AND level <= 5),
    claim_amount DECIMAL(18, 2) NOT NULL,
    reward_amount DECIMAL(18, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_referral_rewards_to_user ON referral_rewards(to_user_id);
CREATE INDEX idx_referral_rewards_from_user ON referral_rewards(from_user_id);
```

---

## Конфигурация

```python
REFERRAL_CONFIG = {
    "levels": {
        1: {"percent": 0.20, "min_active_refs": 0},   # 20%, открыт сразу
        2: {"percent": 0.15, "min_active_refs": 3},   # 15%, от 3 активных
        3: {"percent": 0.10, "min_active_refs": 5},   # 10%, от 5 активных
        4: {"percent": 0.05, "min_active_refs": 10},  # 5%, от 10 активных
        5: {"percent": 0.02, "min_active_refs": 20},  # 2%, от 20 активных
    }
}

def is_active_referral(user):
    """Активный реферал = купил хотя бы 1 пета"""
    return user.pets_bought_count > 0
```

---

## Алгоритм начисления

```python
def process_referral_rewards(claiming_user, claim_amount):
    """
    Вызывается при каждом claim.
    Начисляет реферальные бонусы вверх по цепочке.
    """
    current_user = claiming_user

    for level in range(1, 6):  # levels 1-5
        # Получаем реферрера текущего уровня
        referrer = get_referrer(current_user)
        if not referrer:
            break

        # Проверяем, открыт ли этот уровень у реферрера
        if referrer.ref_levels_unlocked >= level:
            percent = REFERRAL_CONFIG["levels"][level]["percent"]
            reward = claim_amount * percent

            # Начисляем
            referrer.balance_xpet += reward

            # Записываем транзакцию
            create_transaction(
                user_id=referrer.id,
                type="ref_reward",
                amount=reward,
                meta={
                    "from_user_id": claiming_user.id,
                    "level": level,
                    "claim_amount": claim_amount
                }
            )

            # Обновляем статистику
            update_referral_stats(referrer, level, reward)

        current_user = referrer
```

---

## Пример расчёта

```
User A claims 10 XPET profit.

Referral chain (up):
A → B → C → D → E → F

Rewards:
- B (level 1): 10 * 20% = 2 XPET (if B has level 1 unlocked)
- C (level 2): 10 * 15% = 1.5 XPET (if C has level 2 unlocked)
- D (level 3): 10 * 10% = 1 XPET (if D has level 3 unlocked)
- E (level 4): 10 * 5% = 0.5 XPET (if E has level 4 unlocked)
- F (level 5): 10 * 2% = 0.2 XPET (if F has level 5 unlocked)

Total referral payouts: up to 5.2 XPET (52% of claim)
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
