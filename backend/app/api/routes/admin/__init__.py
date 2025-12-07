from fastapi import APIRouter

from app.api.routes.admin import (
    auth,
    users,
    deposits,
    withdrawals,
    pet_types,
    tasks,
    config,
    stats,
    logs,
    broadcast,
)

router = APIRouter(prefix="/admin", tags=["admin"])

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(deposits.router)
router.include_router(withdrawals.router)
router.include_router(pet_types.router)
router.include_router(tasks.router)
router.include_router(config.router)
router.include_router(stats.router)
router.include_router(logs.router)
router.include_router(broadcast.router)
