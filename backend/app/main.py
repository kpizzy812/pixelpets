from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth, pets, wallet, referrals, tasks, telegram_webhook
from app.api.routes.admin import router as admin_router

app = FastAPI(
    title="Pixel Pets API",
    description="Backend API for Pixel Pets Telegram Mini App",
    version="0.1.0",
    debug=settings.DEBUG,
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

# Admin router
app.include_router(admin_router)

# Telegram webhook
app.include_router(telegram_webhook.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
