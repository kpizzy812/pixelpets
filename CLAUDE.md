# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Always use context7 when I need code generation, setup or configuration steps, or
library/API documentation. This means you should automatically use the Context7 MCP
tools to resolve library id and get library docs without me having to explicitly ask.

## Project Overview

Pixel Pets is a Telegram Mini App - an NFT-style economic game where players buy pixel pets, train them for daily rewards, and upgrade them through levels until they reach their ROI cap.

## Tech Stack

- **Frontend**: Next.js + Telegram Mini App SDK (not yet implemented)
- **Backend**: FastAPI (Python) with async SQLAlchemy + asyncpg
- **Database**: PostgreSQL
- **Currency**: XPET (1 XPET = $1 USD)

## Development Commands

### Backend Setup
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Database
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Seed pet types and tasks
python -m app.scripts.seed
```

### Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Tests
```bash
pytest
pytest -v                    # verbose
pytest tests/test_auth.py    # single file
```

## Backend Architecture

```
backend/
├── app/
│   ├── core/           # Config, database, security (JWT/Telegram auth)
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic request/response DTOs
│   ├── services/       # Business logic (auth, pets, wallet, referrals, tasks)
│   ├── api/routes/     # FastAPI routers
│   └── scripts/seed.py # Database seeding
└── alembic/            # Migrations
```

**Pattern**: Routes → Services → Models (layered architecture, all async)

## Core Game Mechanics

### Pet System
- 5 pet types with different daily rates (1.0%-2.5%) and ROI caps (150%-200%)
- 3 levels: Baby → Adult → Mythic
- 3 pet slots per player
- Pet states: OWNED_IDLE, TRAINING, READY_TO_CLAIM, EVOLVED, SOLD

### Training Cycle
- 24-hour training sessions
- Profit = invested_total × daily_rate (capped by roi_cap_multiplier × invested_total)
- After reaching ROI cap, pet evolves and moves to Hall of Fame

### Referral System
- 5 levels deep (20%, 15%, 10%, 5%, 2%)
- Rewards paid from referral claims, not deposits
- Levels unlock based on active referral count

## Key Data Models

- **User**: telegram_id, balance_xpet, ref_code, referrer_id
- **PetType**: base_price, daily_rate, roi_cap_multiplier, level_prices (JSON)
- **UserPet**: invested_total, level, status, profit_claimed, training timestamps
- **Task**: title, reward_xpet, link, task_type, is_active

## API Structure

- `POST /auth/telegram` - Telegram initData authentication
- `GET /auth/me` - Current user profile
- `/pets/*` - buy, upgrade, start-training, claim, sell, hall-of-fame
- `/wallet/*` - balance, deposit/withdraw requests, transactions
- `/referrals/*` - ref link, stats with level breakdown
- `/tasks/*` - task list and completion

## Environment Variables

Required in `backend/.env`:
```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/pixelpets
JWT_SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
```

## Localization

Uses i18n with EN/RU required, plus DE/ES/FR/PT/IT for EU. Language detected from `initData.user.language_code`.
