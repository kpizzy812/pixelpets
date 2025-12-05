# 04. Wallet Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Пополнение и вывод XPET, история транзакций.

---

## Прогресс

### Backend

- [ ] **4.1** Модель Transaction
  - [ ] Создать таблицу transactions
  - [ ] Поля: id, user_id, type, amount_xpet, fee, meta (JSON), status, created_at
  - [ ] Типы: deposit, withdraw, claim, ref_reward, task_reward, sell_refund, admin_adjust, pet_buy, pet_upgrade

- [ ] **4.2** Модель DepositRequest
  - [ ] Таблица deposit_requests
  - [ ] Поля: id, user_id, amount, network, address, status, created_at, confirmed_at

- [ ] **4.3** Модель WithdrawRequest
  - [ ] Таблица withdraw_requests
  - [ ] Поля: id, user_id, amount, fee, network, wallet_address, status, created_at, processed_at

- [ ] **4.4** Deposit Request
  - [ ] Эндпоинт `POST /wallet/deposit-request`
  - [ ] Выбор сети: BEP-20, Solana, TON
  - [ ] Генерация/возврат адреса для оплаты
  - [ ] Статус: pending

- [ ] **4.5** Withdraw Request
  - [ ] Эндпоинт `POST /wallet/withdraw-request`
  - [ ] Минимум: 5 XPET
  - [ ] Расчёт комиссии: $1 + 2%
  - [ ] Проверка баланса (сумма + комиссия)
  - [ ] Списание с баланса
  - [ ] Создание заявки: pending

- [ ] **4.6** Wallet Balance
  - [ ] Эндпоинт `GET /wallet`
  - [ ] Баланс XPET и эквивалент в $

- [ ] **4.7** Transaction History
  - [ ] Эндпоинт `GET /wallet/transactions`
  - [ ] Пагинация
  - [ ] Фильтр по типу

### Frontend

- [ ] **4.8** Wallet Screen
  - [ ] Отображение баланса
  - [ ] Кнопки Deposit / Withdraw

- [ ] **4.9** Deposit Flow
  - [ ] Выбор сети
  - [ ] Ввод суммы
  - [ ] Показ адреса + QR
  - [ ] Статус заявки

- [ ] **4.10** Withdraw Flow
  - [ ] Ввод суммы
  - [ ] Показ комиссии
  - [ ] Ввод адреса кошелька
  - [ ] Подтверждение

- [ ] **4.11** Transaction History UI
  - [ ] Список транзакций
  - [ ] Иконки по типу
  - [ ] Pull-to-refresh

### Tests

- [ ] **4.12** Backend tests
  - [ ] Test deposit request creation
  - [ ] Test withdraw with fee calculation
  - [ ] Test insufficient balance

---

## API Specification

### GET /wallet

**Response 200:**
```json
{
  "balance_xpet": "150.50",
  "balance_usd": "150.50",
  "pending_deposits": 0,
  "pending_withdrawals": 1
}
```

### POST /wallet/deposit-request

**Request:**
```json
{
  "amount": "100.00",
  "network": "BEP-20"
}
```

**Response 200:**
```json
{
  "request_id": 1,
  "amount": "100.00",
  "network": "BEP-20",
  "deposit_address": "0x1234...abcd",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### POST /wallet/withdraw-request

**Request:**
```json
{
  "amount": "50.00",
  "network": "TON",
  "wallet_address": "EQ..."
}
```

**Response 200:**
```json
{
  "request_id": 1,
  "amount": "50.00",
  "fee": "2.00",
  "total_deducted": "52.00",
  "network": "TON",
  "wallet_address": "EQ...",
  "status": "pending",
  "new_balance": "98.50"
}
```

**Errors:**
- 400: Amount below minimum (5 XPET)
- 400: Insufficient balance

### GET /wallet/transactions

**Query params:**
- `page`: int (default 1)
- `limit`: int (default 20)
- `type`: filter by type (optional)

**Response 200:**
```json
{
  "transactions": [
    {
      "id": 1,
      "type": "claim",
      "amount_xpet": "1.50",
      "meta": { "pet_name": "Bubble Slime" },
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "pages": 3
}
```

---

## Data Models

```sql
CREATE TYPE tx_type AS ENUM (
    'deposit', 'withdraw', 'claim', 'ref_reward',
    'task_reward', 'sell_refund', 'admin_adjust',
    'pet_buy', 'pet_upgrade'
);

CREATE TYPE tx_status AS ENUM ('pending', 'completed', 'failed', 'cancelled');

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    type tx_type NOT NULL,
    amount_xpet DECIMAL(18, 2) NOT NULL,
    fee DECIMAL(18, 2) DEFAULT 0,
    meta JSONB,
    status tx_status DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE network_type AS ENUM ('BEP-20', 'Solana', 'TON');
CREATE TYPE request_status AS ENUM ('pending', 'approved', 'rejected', 'completed');

CREATE TABLE deposit_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    network network_type NOT NULL,
    deposit_address VARCHAR(255),
    status request_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP,
    confirmed_by INTEGER REFERENCES users(id)
);

CREATE TABLE withdraw_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    fee DECIMAL(18, 2) NOT NULL,
    network network_type NOT NULL,
    wallet_address VARCHAR(255) NOT NULL,
    status request_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    processed_by INTEGER REFERENCES users(id)
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(type);
CREATE INDEX idx_deposit_requests_status ON deposit_requests(status);
CREATE INDEX idx_withdraw_requests_status ON withdraw_requests(status);
```

---

## Комиссия вывода

```python
WITHDRAW_MIN = 5  # XPET
WITHDRAW_FEE_FIXED = 1  # $1
WITHDRAW_FEE_PERCENT = 0.02  # 2%

def calculate_withdraw_fee(amount):
    return WITHDRAW_FEE_FIXED + (amount * WITHDRAW_FEE_PERCENT)

# Example:
# amount = 50 XPET
# fee = 1 + (50 * 0.02) = 1 + 1 = 2 XPET
# total_deducted = 52 XPET
```

---

## Сети для депозита/вывода

| Network | Currency | Address Format |
|---------|----------|----------------|
| BEP-20 | USDT | 0x... (42 chars) |
| Solana | USDT | Base58 (32-44 chars) |
| TON | USDT | EQ... or UQ... |

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
