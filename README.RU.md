<p align="center">
  <img src="assets/banner.png" alt="Pixel Pets Banner" width="100%">
</p>

<h1 align="center">Pixel Pets</h1>

<p align="center">
  <strong>Telegram Mini App — экономическая игра с NFT-механикой и ежедневными наградами</strong>
</p>

<p align="center">
  <a href="https://t.me/Pixel_PetsBot?startapp">
    <img src="https://img.shields.io/badge/Telegram-Играть-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Играть в Telegram">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Next.js-16-000000?style=flat-square&logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Статус-Production-brightgreen?style=flat-square" alt="Статус">
  <img src="https://img.shields.io/badge/Лицензия-MIT-green?style=flat-square" alt="Лицензия">
  <img src="https://img.shields.io/badge/i18n-7%20языков-blue?style=flat-square" alt="Языки">
</p>

<p align="center">
  <a href="README.md">English version</a>
</p>

---

## О проекте

**Pixel Pets** — это Telegram Mini App, где игроки покупают пиксельных питомцев, тренируют их для ежедневного дохода и прокачивают через уровни эволюции до достижения максимального ROI.

**Игровой цикл:** Купить питомца → Тренировать ежедневно → Забирать награды → Прокачивать → Попасть в Зал Славы

## Возможности

- **Система питомцев** — 6 уникальных типов с разной доходностью (1.0%–2.5%) и ROI-кэпами (150%–200%)
- **Эволюция** — 3 уровня: Baby → Adult → Mythic
- **Цикл тренировки** — 24-часовые сессии с наградами
- **5-уровневые рефералы** — Заработок от сети (20% → 15% → 10% → 5% → 2%)
- **Мультичейн кошелёк** — Депозит/вывод через BEP-20, Solana, TON
- **Lucky Spin** — Ежедневное колесо удачи для бонусов
- **Зал Славы** — Витрина питомцев, достигших максимального ROI
- **Локализация** — 7 языков (EN, RU, DE, ES, FR, PT, IT)

## Технологии

| Слой | Технологии |
|------|------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Zustand |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic, Alembic |
| **База данных** | PostgreSQL + asyncpg |
| **Авторизация** | JWT + Telegram WebApp signature verification |
| **Админка** | Отдельное Next.js приложение с Radix UI, React Query, React Hook Form |
| **Уведомления** | Telegram Bot API для напоминаний о тренировке |

## Структура проекта

```
├── backend/          # FastAPI REST API
│   ├── app/
│   │   ├── api/      # Обработчики маршрутов
│   │   ├── core/     # Конфигурация, БД, безопасность
│   │   ├── models/   # SQLAlchemy ORM модели
│   │   ├── schemas/  # Pydantic DTO
│   │   ├── services/ # Бизнес-логика
│   │   └── i18n/     # Переводы
│   ├── alembic/      # Миграции базы данных
│   └── tests/        # Тесты (pytest)
│
├── frontend/         # Telegram Mini App (Next.js)
│   ├── app/          # Страницы App Router
│   ├── components/   # React компоненты
│   ├── lib/          # API клиент, утилиты
│   ├── store/        # Zustand состояние
│   └── messages/     # i18n переводы
│
└── admin-panel/      # Админ-панель (Next.js)
    ├── app/          # Маршруты дашборда
    ├── components/   # UI компоненты (Radix)
    └── lib/          # API клиент
```

## Быстрый старт

### Требования

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Настройка .env
cp .env.example .env

# Миграции
alembic upgrade head

# Начальные данные
python -m app.scripts.seed

# Запуск
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Админ-панель

```bash
cd admin-panel
npm install
npm run dev -- -p 3001
```

## API Endpoints

| Endpoint | Описание |
|----------|----------|
| `POST /auth/telegram` | Авторизация через Telegram initData |
| `GET /pets/types` | Получить типы питомцев |
| `POST /pets/buy` | Купить питомца |
| `POST /pets/{id}/start-training` | Начать 24ч тренировку |
| `POST /pets/{id}/claim` | Забрать награды |
| `GET /referrals/stats` | Статистика рефералов |
| `GET /tasks` | Список заданий |
| `POST /wallet/deposit` | Запрос адреса для депозита |

## Переменные окружения

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/pixelpets
JWT_SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Лицензия

MIT License — см. [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://t.me/Pixel_PetsBot?startapp">
    <img src="https://img.shields.io/badge/Играть%20в%20Pixel%20Pets-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Играть в Telegram">
  </a>
</p>
