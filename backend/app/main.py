import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_session
from app.api.routes import auth, pets, wallet, referrals, tasks, spin, telegram_webhook, boosts, syntra
from app.api.routes.admin import router as admin_router
from app.services.auto_claim import run_auto_claim_job
from app.services.training_notifications import run_training_notification_job
from app.services.admin.broadcast import run_broadcast_scheduler
from app.services.admin.config import init_default_configs

logger = logging.getLogger(__name__)

# Scheduler settings
AUTO_CLAIM_INTERVAL_MINUTES = 5
TRAINING_NOTIFICATION_INTERVAL_MINUTES = 5
BROADCAST_SCHEDULER_INTERVAL_MINUTES = 1  # Check every minute for scheduled broadcasts


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


async def training_notification_scheduler():
    """Background task that sends training complete notifications every N minutes."""
    while True:
        try:
            await asyncio.sleep(TRAINING_NOTIFICATION_INTERVAL_MINUTES * 60)

            async with async_session() as db:
                stats = await run_training_notification_job(db)
                if stats["processed"] > 0:
                    logger.info(f"Training notifications sent: {stats}")
        except asyncio.CancelledError:
            logger.info("Training notification scheduler stopped")
            break
        except Exception as e:
            logger.error(f"Training notification scheduler error: {e}")
            # Continue running despite errors
            await asyncio.sleep(60)  # Wait a bit before retrying


async def broadcast_scheduler():
    """Background task that checks and sends scheduled broadcasts."""
    while True:
        try:
            await asyncio.sleep(BROADCAST_SCHEDULER_INTERVAL_MINUTES * 60)

            async with async_session() as db:
                stats = await run_broadcast_scheduler(db)
                if stats["processed"] > 0:
                    logger.info(f"Broadcast scheduler completed: {stats}")
        except asyncio.CancelledError:
            logger.info("Broadcast scheduler stopped")
            break
        except Exception as e:
            logger.error(f"Broadcast scheduler error: {e}")
            await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - start/stop background tasks."""
    # Initialize default configs on startup
    async with async_session() as db:
        await init_default_configs(db)
        logger.info("Default configs initialized")

    # Start schedulers
    auto_claim_task = asyncio.create_task(auto_claim_scheduler())
    training_notification_task = asyncio.create_task(training_notification_scheduler())
    broadcast_task = asyncio.create_task(broadcast_scheduler())
    logger.info("Auto-claim scheduler started")
    logger.info("Training notification scheduler started")
    logger.info("Broadcast scheduler started")

    yield

    # Stop schedulers on shutdown
    auto_claim_task.cancel()
    training_notification_task.cancel()
    broadcast_task.cancel()
    try:
        await auto_claim_task
    except asyncio.CancelledError:
        pass
    try:
        await training_notification_task
    except asyncio.CancelledError:
        pass
    try:
        await broadcast_task
    except asyncio.CancelledError:
        pass
    logger.info("Auto-claim scheduler stopped")
    logger.info("Training notification scheduler stopped")
    logger.info("Broadcast scheduler stopped")


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

# Syntra integration
app.include_router(syntra.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
