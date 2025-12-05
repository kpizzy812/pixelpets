from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.enums import NetworkType, TxType, RequestStatus


class WalletResponse(BaseModel):
    balance_xpet: Decimal
    balance_usd: Decimal
    pending_deposits: int
    pending_withdrawals: int


class DepositRequestCreate(BaseModel):
    amount: Decimal
    network: NetworkType


class DepositRequestResponse(BaseModel):
    request_id: int
    amount: Decimal
    network: NetworkType
    deposit_address: Optional[str]
    status: RequestStatus
    created_at: datetime


class WithdrawRequestCreate(BaseModel):
    amount: Decimal
    network: NetworkType
    wallet_address: str


class WithdrawRequestResponse(BaseModel):
    request_id: int
    amount: Decimal
    fee: Decimal
    total_deducted: Decimal
    network: NetworkType
    wallet_address: str
    status: RequestStatus
    new_balance: Decimal


class TransactionResponse(BaseModel):
    id: int
    type: TxType
    amount_xpet: Decimal
    fee: Decimal
    meta: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionsListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    page: int
    pages: int
