# 06. Tasks Module

[← Назад к PROGRESS.md](../PROGRESS.md)

---

## Описание

Система заданий с наградами XPET (подписка на каналы и др.).

---

## Прогресс

### Backend

- [ ] **6.1** Модель Task
  - [ ] Создать таблицу tasks
  - [ ] Поля: id, title, description, reward_xpet, link, task_type, is_active, order, created_at

- [ ] **6.2** Модель UserTask
  - [ ] Таблица user_tasks
  - [ ] Поля: id, user_id, task_id, status, completed_at
  - [ ] Статусы: pending, completed

- [ ] **6.3** Task List
  - [ ] Эндпоинт `GET /tasks`
  - [ ] Список активных задач
  - [ ] Статус выполнения для текущего пользователя

- [ ] **6.4** Task Check/Complete
  - [ ] Эндпоинт `POST /tasks/check`
  - [ ] Проверка выполнения (опционально: через Telegram API для каналов)
  - [ ] Начисление награды
  - [ ] Запись транзакции

- [ ] **6.5** Telegram Channel Check (опционально)
  - [ ] Интеграция с Telegram Bot API
  - [ ] getChatMember для проверки подписки
  - [ ] Fallback: доверять клику (без проверки)

### Frontend

- [ ] **6.6** Tasks Screen
  - [ ] Список задач
  - [ ] Иконки по типу (TG, Twitter, etc.)
  - [ ] Награды

- [ ] **6.7** Task Item Component
  - [ ] Кнопка "Go" → открывает ссылку
  - [ ] После возврата: кнопка "Check"
  - [ ] Completed → галочка

- [ ] **6.8** Completed Tasks Section
  - [ ] Отдельный блок или сортировка вниз

### Tests

- [ ] **6.9** Backend tests
  - [ ] Test task list
  - [ ] Test task completion
  - [ ] Test duplicate completion prevention

---

## API Specification

### GET /tasks

**Response 200:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Join our Telegram",
      "description": "Subscribe to official channel",
      "reward_xpet": "0.30",
      "link": "https://t.me/pixelpets_official",
      "task_type": "telegram_channel",
      "is_completed": false
    },
    {
      "id": 2,
      "title": "Follow on Twitter",
      "description": "Follow @pixelpets",
      "reward_xpet": "0.20",
      "link": "https://twitter.com/pixelpets",
      "task_type": "twitter",
      "is_completed": true,
      "completed_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total_earned": "0.50",
  "available_count": 3,
  "completed_count": 2
}
```

### POST /tasks/check

**Request:**
```json
{
  "task_id": 1
}
```

**Response 200:**
```json
{
  "success": true,
  "reward_xpet": "0.30",
  "new_balance": "150.80",
  "message": "Task completed!"
}
```

**Errors:**
- 400: Task already completed
- 400: Task verification failed (if verification enabled)
- 404: Task not found

---

## Data Models

```sql
CREATE TYPE task_type AS ENUM (
    'telegram_channel',
    'telegram_chat',
    'twitter',
    'discord',
    'website',
    'other'
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    reward_xpet DECIMAL(18, 2) NOT NULL,
    link VARCHAR(500),
    task_type task_type DEFAULT 'other',
    verification_data JSONB,  -- e.g., {"channel_id": "@pixelpets"}
    is_active BOOLEAN DEFAULT true,
    "order" INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TYPE task_status AS ENUM ('pending', 'completed');

CREATE TABLE user_tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    task_id INTEGER REFERENCES tasks(id) NOT NULL,
    status task_status DEFAULT 'pending',
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, task_id)
);

CREATE INDEX idx_tasks_active ON tasks(is_active);
CREATE INDEX idx_user_tasks_user_id ON user_tasks(user_id);
```

---

## Seed Data

```sql
INSERT INTO tasks (title, description, reward_xpet, link, task_type, "order") VALUES
('Join Telegram Channel', 'Subscribe to our official channel', 0.30, 'https://t.me/pixelpets_official', 'telegram_channel', 1),
('Join Telegram Chat', 'Join community chat', 0.20, 'https://t.me/pixelpets_chat', 'telegram_chat', 2),
('Follow on Twitter', 'Follow @pixelpets', 0.20, 'https://twitter.com/pixelpets', 'twitter', 3),
('Retweet Announcement', 'Retweet our pinned post', 0.10, 'https://twitter.com/pixelpets/status/123', 'twitter', 4),
('Visit Website', 'Check out our website', 0.10, 'https://pixelpets.io', 'website', 5);
```

---

## Верификация Telegram (опционально)

```python
import requests

async def verify_telegram_subscription(user_telegram_id: int, channel_username: str) -> bool:
    """
    Проверка подписки на Telegram канал через Bot API.
    Требует, чтобы бот был админом канала.
    """
    BOT_TOKEN = "your_bot_token"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
    params = {
        "chat_id": f"@{channel_username}",
        "user_id": user_telegram_id
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("ok"):
        status = data["result"]["status"]
        # member, administrator, creator = subscribed
        return status in ["member", "administrator", "creator"]

    return False
```

---

## UI Flow

```
Tasks Screen
┌─────────────────────────────────────┐
│  📋 Tasks                           │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 📢 Join Telegram Channel    │    │
│  │    +0.30 XPET              │    │
│  │              [Go] [Check]   │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🐦 Follow on Twitter   ✓   │    │
│  │    +0.20 XPET (claimed)    │    │
│  └─────────────────────────────┘    │
│                                     │
│  ─────── Completed (2) ───────      │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ 🌐 Visit Website       ✓   │    │
│  │    +0.10 XPET              │    │
│  └─────────────────────────────┘    │
│                                     │
└─────────────────────────────────────┘
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
