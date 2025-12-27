<p align="center">
  <img src="assets/banner.png" alt="Pixel Pets Banner" width="100%">
</p>

<h1 align="center">Pixel Pets</h1>

<p align="center">
  <strong>Telegram Mini App — NFT-style economic game with daily rewards</strong>
</p>

<p align="center">
  <a href="https://t.me/Pixel_PetsBot?startapp">
    <img src="https://img.shields.io/badge/Telegram-Play%20Now-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Play on Telegram">
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
  <img src="https://img.shields.io/badge/Status-Production-brightgreen?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/i18n-7%20languages-blue?style=flat-square" alt="Languages">
</p>

<p align="center">
  <a href="README.RU.md">Русская версия</a>
</p>

---

## About

**Pixel Pets** is a Telegram Mini App where players buy pixel pets, train them for daily rewards, and upgrade them through evolution levels until they reach their ROI cap.

**Core loop:** Buy a pet → Train daily → Claim rewards → Upgrade → Reach Hall of Fame

## Features

- **Pet System** — 6 unique pet types with different daily rates (1.0%–2.5%) and ROI caps (150%–200%)
- **Evolution** — 3 levels: Baby → Adult → Mythic
- **Training Cycle** — 24-hour sessions with claimable rewards
- **5-Level Referrals** — Earn from your network (20% → 15% → 10% → 5% → 2%)
- **Multi-Chain Wallet** — Deposit/withdraw via BEP-20, Solana, TON
- **Lucky Spin** — Daily spin wheel for bonus rewards
- **Hall of Fame** — Showcase evolved pets that reached max ROI
- **Localization** — 7 languages (EN, RU, DE, ES, FR, PT, IT)

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS 4, Zustand |
| **Backend** | FastAPI, SQLAlchemy (async), Pydantic, Alembic |
| **Database** | PostgreSQL + asyncpg |
| **Auth** | JWT + Telegram WebApp signature verification |
| **Admin** | Separate Next.js app with Radix UI, React Query, React Hook Form |
| **Notifications** | Telegram Bot API for training reminders |

## Project Structure

```
├── backend/          # FastAPI REST API
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, database, security
│   │   ├── models/   # SQLAlchemy ORM models
│   │   ├── schemas/  # Pydantic DTOs
│   │   ├── services/ # Business logic
│   │   └── i18n/     # Translations
│   ├── alembic/      # Database migrations
│   └── tests/        # Pytest test suite
│
├── frontend/         # Telegram Mini App (Next.js)
│   ├── app/          # App Router pages
│   ├── components/   # React components
│   ├── lib/          # API client, utilities
│   ├── store/        # Zustand state
│   └── messages/     # i18n translations
│
└── admin-panel/      # Admin dashboard (Next.js)
    ├── app/          # Dashboard routes
    ├── components/   # UI components (Radix)
    └── lib/          # API client
```

## Getting Started

### Prerequisites

- Node.js 20+
- Python 3.12+
- PostgreSQL 16+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed data
python -m app.scripts.seed

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Admin Panel

```bash
cd admin-panel
npm install
npm run dev -- -p 3001
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /auth/telegram` | Authenticate via Telegram initData |
| `GET /pets/types` | Get available pet types |
| `POST /pets/buy` | Purchase a new pet |
| `POST /pets/{id}/start-training` | Start 24h training |
| `POST /pets/{id}/claim` | Claim training rewards |
| `GET /referrals/stats` | Get referral statistics |
| `GET /tasks` | Get available tasks |
| `POST /wallet/deposit` | Request deposit address |

## Environment Variables

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/pixelpets
JWT_SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://t.me/Pixel_PetsBot?startapp">
    <img src="https://img.shields.io/badge/Play%20Pixel%20Pets-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Play on Telegram">
  </a>
</p>
