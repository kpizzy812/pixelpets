import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_session
from app.api.routes import auth, pets, wallet, referrals, tasks, spin, telegram_webhook, boosts
from app.api.routes.admin import router as admin_router
from app.services.auto_claim import run_auto_claim_job

logger = logging.getLogger(__name__)

# Auto-claim scheduler settings
AUTO_CLAIM_INTERVAL_MINUTES = 5


async def auto_claim_scheduler():
    """Background task that runs auto-claim every N minutes."""
    while True:
        try:
            await asyncio.sleep(AUTO_CLAIM_INTERVAL_MINUTES * 60)

            async with async_session() as db:
                stats = await run_auto_claim_job(db)
                if stats["processed"] > 0:
                    logger.info(f"Auto-claim completed: {stats}")
        except asyncio.CancelledError:
            logger.info("Auto-claim scheduler stopped")
            break
        except Exception as e:
            logger.error(f"Auto-claim scheduler error: {e}")
            # Continue running despite errors
            await asyncio.sleep(60)  # Wait a bit before retrying


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - start/stop background tasks."""
    # Start auto-claim scheduler
    scheduler_task = asyncio.create_task(auto_claim_scheduler())
    logger.info("Auto-claim scheduler started")

    yield

    # Stop scheduler on shutdown
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    logger.info("Auto-claim scheduler stopped")


app = FastAPI(
    title="Pixel Pets API",
    description="Backend API for Pixel Pets Telegram Mini App",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User-facing routers
app.include_router(auth.router)
app.include_router(pets.router)
app.include_router(wallet.router)
app.include_router(referrals.router)
app.include_router(tasks.router)
app.include_router(spin.router)
app.include_router(boosts.router)

# Admin router
app.include_router(admin_router)

# Telegram webhook
app.include_router(telegram_webhook.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
