from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import (
    AdminRole,
    RequestStatus,
    NetworkType,
    PetStatus,
    PetLevel,
    TaskType,
)


# ============ Admin Auth ============

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: "AdminResponse"


class AdminResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: AdminRole
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    role: AdminRole = AdminRole.MODERATOR


class AdminUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


# ============ Users Management ============

class UserListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    search: Optional[str] = None  # Search by telegram_id, username, ref_code
    order_by: str = "created_at"
    order_desc: bool = True


class UserDetailResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    language_code: str
    balance_xpet: Decimal
    ref_code: str
    referrer_id: Optional[int]
    ref_levels_unlocked: int
    created_at: datetime
    updated_at: datetime
    # Stats
    total_deposited: Decimal = Decimal("0")
    total_withdrawn: Decimal = Decimal("0")
    total_claimed: Decimal = Decimal("0")
    total_ref_earned: Decimal = Decimal("0")
    active_pets_count: int = 0
    referrals_count: int = 0

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserDetailResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class BalanceAdjustRequest(BaseModel):
    amount: Decimal  # Positive = add, negative = subtract
    reason: str = Field(..., min_length=1, max_length=500)


class BalanceAdjustResponse(BaseModel):
    user_id: int
    old_balance: Decimal
    new_balance: Decimal
    amount: Decimal
    reason: str
    transaction_id: int


# ============ Deposits ============

class DepositListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    status: Optional[RequestStatus] = None
    network: Optional[NetworkType] = None
    user_id: Optional[int] = None


class DepositDetailResponse(BaseModel):
    id: int
    user_id: int
    telegram_id: int
    username: Optional[str]
    amount: Decimal
    network: NetworkType
    deposit_address: Optional[str]
    status: RequestStatus
    created_at: datetime
    confirmed_at: Optional[datetime]
    confirmed_by: Optional[int]

    class Config:
        from_attributes = True


class DepositListResponse(BaseModel):
    deposits: List[DepositDetailResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class DepositActionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    note: Optional[str] = None


# ============ Withdrawals ============

class WithdrawalListRequest(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)
    status: Optional[RequestStatus] = None
    network: Optional[NetworkType] = None
    user_id: Optional[int] = None


class WithdrawalDetailResponse(BaseModel):
    id: int
    user_id: int
    telegram_id: int
    username: Optional[str]
    amount: Decimal
    fee: Decimal
    net_amount: Decimal  # amount - fee
    network: NetworkType
    wallet_address: str
    status: RequestStatus
    created_at: datetime
    processed_at: Optional[datetime]
    processed_by: Optional[int]

    class Config:
        from_attributes = True


class WithdrawalListResponse(BaseModel):
    withdrawals: List[WithdrawalDetailResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class WithdrawalActionRequest(BaseModel):
    action: str = Field(..., pattern="^(complete|reject)$")
    tx_hash: Optional[str] = None  # For completed withdrawals
    note: Optional[str] = None


# ============ Pet Types ============

class PetTypeResponse(BaseModel):
    id: int
    name: str
    emoji: Optional[str]
    base_price: Decimal
    daily_rate: Decimal
    roi_cap_multiplier: Decimal
    level_prices: dict
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PetTypeCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    emoji: Optional[str] = None
    base_price: Decimal = Field(..., gt=0)
    daily_rate: Decimal = Field(..., gt=0, le=1)  # 0.01 = 1%
    roi_cap_multiplier: Decimal = Field(..., gt=1)  # 1.5 = 150%
    level_prices: dict = Field(
        ...,
        description="e.g. {'BABY': 5, 'ADULT': 15, 'MYTHIC': 30}"
    )
    is_active: bool = True


class PetTypeUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    emoji: Optional[str] = None
    base_price: Optional[Decimal] = Field(None, gt=0)
    daily_rate: Optional[Decimal] = Field(None, gt=0, le=1)
    roi_cap_multiplier: Optional[Decimal] = Field(None, gt=1)
    level_prices: Optional[dict] = None
    is_active: Optional[bool] = None


# ============ Tasks ============

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    reward_xpet: Decimal
    link: Optional[str]
    task_type: TaskType
    verification_data: Optional[dict]
    is_active: bool
    order: int
    created_at: datetime
    updated_at: datetime
    completions_count: int = 0

    class Config:
        from_attributes = True


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    reward_xpet: Decimal = Field(..., gt=0)
    link: Optional[str] = None
    task_type: TaskType = TaskType.OTHER
    verification_data: Optional[dict] = None
    is_active: bool = True
    order: int = 0


class TaskUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    reward_xpet: Optional[Decimal] = Field(None, gt=0)
    link: Optional[str] = None
    task_type: Optional[TaskType] = None
    verification_data: Optional[dict] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int


# ============ System Config ============

class ConfigItemResponse(BaseModel):
    id: int
    key: str
    value: Any
    description: Optional[str]
    updated_at: datetime

    class Config:
        from_attributes = True


class ConfigUpdateRequest(BaseModel):
    value: Any
    description: Optional[str] = None


class ReferralConfigResponse(BaseModel):
    percentages: dict  # {"1": 20, "2": 15, ...}
    unlock_thresholds: dict  # {"1": 0, "2": 3, ...}


class ReferralConfigUpdateRequest(BaseModel):
    percentages: Optional[dict] = None
    unlock_thresholds: Optional[dict] = None


# ============ Dashboard Stats ============

class DashboardStatsResponse(BaseModel):
    # Users
    total_users: int
    new_users_today: int
    new_users_week: int
    active_users_today: int

    # Finance
    total_balance_xpet: Decimal
    pending_deposits_count: int
    pending_deposits_amount: Decimal
    pending_withdrawals_count: int
    pending_withdrawals_amount: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal

    # Pets
    total_pets_active: int
    total_pets_evolved: int
    total_claimed_xpet: Decimal

    # Referrals
    total_ref_rewards_paid: Decimal

    # Tasks
    total_task_rewards_paid: Decimal


class AdminActionLogResponse(BaseModel):
    id: int
    admin_id: int
    admin_username: str
    action: str
    target_type: Optional[str]
    target_id: Optional[int]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AdminActionLogListResponse(BaseModel):
    logs: List[AdminActionLogResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# Forward reference update
AdminLoginResponse.model_rebuild()
