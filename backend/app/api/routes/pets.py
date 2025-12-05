from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.enums import PetStatus
from app.schemas.pet import (
    PetCatalogResponse,
    PetTypeResponse,
    MyPetsResponse,
    UserPetResponse,
    BuyPetRequest,
    BuyPetResponse,
    PetIdRequest,
    UpgradePetResponse,
    SellPetResponse,
    StartTrainingResponse,
    ClaimResponse,
    HallOfFameResponse,
    HallOfFameEntry,
)
from app.services.pets import (
    get_pet_catalog,
    get_user_pets,
    buy_pet,
    upgrade_pet,
    sell_pet,
    start_training,
    claim_profit,
    get_hall_of_fame,
    check_training_status,
    get_next_level,
    calculate_max_profit,
    calculate_upgrade_cost,
    MAX_SLOTS,
)

router = APIRouter(prefix="/pets", tags=["pets"])


def pet_to_response(pet) -> UserPetResponse:
    """Convert UserPet model to response schema."""
    # Check training status
    pet = check_training_status(pet)

    max_profit = calculate_max_profit(pet.invested_total, pet.pet_type.roi_cap_multiplier)
    next_level = get_next_level(pet.level)
    upgrade_cost = None
    if next_level and pet.status not in [PetStatus.EVOLVED, PetStatus.SOLD]:
        upgrade_cost = calculate_upgrade_cost(pet.pet_type.level_prices, next_level, pet.invested_total)

    return UserPetResponse(
        id=pet.id,
        pet_type=PetTypeResponse.model_validate(pet.pet_type),
        invested_total=pet.invested_total,
        level=pet.level,
        status=pet.status,
        slot_index=pet.slot_index,
        profit_claimed=pet.profit_claimed,
        max_profit=max_profit,
        training_started_at=pet.training_started_at,
        training_ends_at=pet.training_ends_at,
        upgrade_cost=upgrade_cost,
        next_level=next_level,
    )


@router.get("/catalog", response_model=PetCatalogResponse)
async def get_catalog(db: AsyncSession = Depends(get_db)):
    """Get all available pet types."""
    pet_types = await get_pet_catalog(db)
    return PetCatalogResponse(
        pets=[PetTypeResponse.model_validate(pt) for pt in pet_types]
    )


@router.get("/my", response_model=MyPetsResponse)
async def get_my_pets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's pets."""
    pets = await get_user_pets(db, current_user.id)

    return MyPetsResponse(
        pets=[pet_to_response(pet) for pet in pets],
        slots_used=len(pets),
        max_slots=MAX_SLOTS,
    )


@router.post("/buy", response_model=BuyPetResponse)
async def buy_pet_endpoint(
    request: BuyPetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Buy a new pet."""
    try:
        pet, new_balance = await buy_pet(db, current_user, request.pet_type_id)
        return BuyPetResponse(
            pet=pet_to_response(pet),
            new_balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/upgrade", response_model=UpgradePetResponse)
async def upgrade_pet_endpoint(
    request: PetIdRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upgrade a pet to the next level."""
    try:
        pet, new_balance = await upgrade_pet(db, current_user, request.pet_id)
        return UpgradePetResponse(
            pet=pet_to_response(pet),
            new_balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sell", response_model=SellPetResponse)
async def sell_pet_endpoint(
    request: PetIdRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sell a pet for 85% refund."""
    try:
        refund_amount, new_balance = await sell_pet(db, current_user, request.pet_id)
        return SellPetResponse(
            refund_amount=refund_amount,
            new_balance=new_balance,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/start-training", response_model=StartTrainingResponse)
async def start_training_endpoint(
    request: PetIdRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start 24h training for a pet."""
    try:
        pet = await start_training(db, current_user, request.pet_id)
        return StartTrainingResponse(
            pet_id=pet.id,
            status=pet.status,
            training_started_at=pet.training_started_at,
            training_ends_at=pet.training_ends_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/claim", response_model=ClaimResponse)
async def claim_endpoint(
    request: PetIdRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Claim daily profit from a pet."""
    try:
        result = await claim_profit(db, current_user, request.pet_id)
        return ClaimResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/hall-of-fame", response_model=HallOfFameResponse)
async def get_hall_of_fame_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's evolved pets (Hall of Fame)."""
    data = await get_hall_of_fame(db, current_user.id)

    entries = []
    for pet in data["pets"]:
        lifetime_days = (pet.evolved_at - pet.created_at).days if pet.evolved_at else 0
        entries.append(HallOfFameEntry(
            id=pet.id,
            pet_type=PetTypeResponse.model_validate(pet.pet_type),
            final_level=pet.level,
            invested_total=pet.invested_total,
            total_farmed=pet.profit_claimed,
            lifetime_days=lifetime_days,
            evolved_at=pet.evolved_at,
        ))

    return HallOfFameResponse(
        pets=entries,
        total_pets_evolved=data["total_pets_evolved"],
        total_farmed_all_time=data["total_farmed_all_time"],
    )
