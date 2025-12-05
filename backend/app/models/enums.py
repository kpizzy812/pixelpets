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
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    CLAIM = "CLAIM"
    REF_REWARD = "REF_REWARD"
    TASK_REWARD = "TASK_REWARD"
    SELL_REFUND = "SELL_REFUND"
    ADMIN_ADJUST = "ADMIN_ADJUST"
    PET_BUY = "PET_BUY"
    PET_UPGRADE = "PET_UPGRADE"
    WITHDRAW_REFUND = "WITHDRAW_REFUND"
    SPIN_COST = "SPIN_COST"
    SPIN_WIN = "SPIN_WIN"
    BOOST_PURCHASE = "BOOST_PURCHASE"
    AUTO_CLAIM_COMMISSION = "AUTO_CLAIM_COMMISSION"


class TxStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class NetworkType(str, enum.Enum):
    BEP20 = "BEP-20"
    SOLANA = "Solana"
    TON = "TON"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class TaskType(str, enum.Enum):
    TELEGRAM_CHANNEL = "TELEGRAM_CHANNEL"
    TELEGRAM_CHAT = "TELEGRAM_CHAT"
    TWITTER = "TWITTER"
    DISCORD = "DISCORD"
    WEBSITE = "WEBSITE"
    OTHER = "OTHER"


class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class AdminRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"  # Full access
    ADMIN = "admin"  # Can manage users, deposits, withdrawals
    MODERATOR = "moderator"  # Can only view, limited actions


class SpinRewardType(str, enum.Enum):
    XPET = "XPET"  # Fixed XPET amount
    NOTHING = "NOTHING"  # No reward (try again)
    BONUS_PERCENT = "BONUS_PERCENT"  # % bonus to next claim


class SnackType(str, enum.Enum):
    COOKIE = "COOKIE"  # +10% bonus
    STEAK = "STEAK"  # +25% bonus
    CAKE = "CAKE"  # +50% bonus


class BoostType(str, enum.Enum):
    ROI_BOOST = "ROI_BOOST"  # Permanent ROI cap increase
    SNACK = "SNACK"  # One-time claim bonus
    AUTO_CLAIM = "AUTO_CLAIM"  # Auto-claim subscription
