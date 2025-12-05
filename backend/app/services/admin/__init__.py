from app.services.admin.auth import (
    authenticate_admin,
    create_admin,
    get_admin_by_id,
    update_admin,
    hash_password,
    verify_password,
)
from app.services.admin.users import (
    get_users_list,
    get_user_detail,
    adjust_user_balance,
)
from app.services.admin.deposits import (
    get_deposits_list,
    approve_deposit,
    reject_deposit,
)
from app.services.admin.withdrawals import (
    get_withdrawals_list,
    complete_withdrawal,
    reject_withdrawal,
)
from app.services.admin.pet_types import (
    get_pet_types,
    create_pet_type,
    update_pet_type,
    delete_pet_type,
)
from app.services.admin.tasks import (
    get_all_tasks,
    create_task,
    update_task,
    delete_task,
)
from app.services.admin.config import (
    get_config,
    set_config,
    get_referral_config,
    update_referral_config,
)
from app.services.admin.stats import get_dashboard_stats
from app.services.admin.logs import log_admin_action, get_admin_logs

__all__ = [
    # Auth
    "authenticate_admin",
    "create_admin",
    "get_admin_by_id",
    "update_admin",
    "hash_password",
    "verify_password",
    # Users
    "get_users_list",
    "get_user_detail",
    "adjust_user_balance",
    # Deposits
    "get_deposits_list",
    "approve_deposit",
    "reject_deposit",
    # Withdrawals
    "get_withdrawals_list",
    "complete_withdrawal",
    "reject_withdrawal",
    # Pet Types
    "get_pet_types",
    "create_pet_type",
    "update_pet_type",
    "delete_pet_type",
    # Tasks
    "get_all_tasks",
    "create_task",
    "update_task",
    "delete_task",
    # Config
    "get_config",
    "set_config",
    "get_referral_config",
    "update_referral_config",
    # Stats
    "get_dashboard_stats",
    # Logs
    "log_admin_action",
    "get_admin_logs",
]
