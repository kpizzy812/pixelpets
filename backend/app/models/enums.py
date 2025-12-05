import enum


class PetStatus(str, enum.Enum):
    OWNED_IDLE = "OWNED_IDLE"
    TRAINING = "TRAINING"
    READY_TO_CLAIM = "READY_TO_CLAIM"
    EVOLVED = "EVOLVED"
    SOLD = "SOLD"


class PetLevel(str, enum.Enum):
    BABY = "BABY"
    ADULT = "ADULT"
    MYTHIC = "MYTHIC"


class TxType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    CLAIM = "claim"
    REF_REWARD = "ref_reward"
    TASK_REWARD = "task_reward"
    SELL_REFUND = "sell_refund"
    ADMIN_ADJUST = "admin_adjust"
    PET_BUY = "pet_buy"
    PET_UPGRADE = "pet_upgrade"
    WITHDRAW_REFUND = "withdraw_refund"
    SPIN_COST = "spin_cost"
    SPIN_WIN = "spin_win"


class TxStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NetworkType(str, enum.Enum):
    BEP20 = "BEP-20"
    SOLANA = "Solana"
    TON = "TON"


class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class TaskType(str, enum.Enum):
    TELEGRAM_CHANNEL = "telegram_channel"
    TELEGRAM_CHAT = "telegram_chat"
    TWITTER = "twitter"
    DISCORD = "discord"
    WEBSITE = "website"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"  # Full access
    ADMIN = "admin"  # Can manage users, deposits, withdrawals
    MODERATOR = "moderator"  # Can only view, limited actions


class SpinRewardType(str, enum.Enum):
    XPET = "xpet"  # Fixed XPET amount
    NOTHING = "nothing"  # No reward (try again)
    BONUS_PERCENT = "bonus_percent"  # % bonus to next claim
