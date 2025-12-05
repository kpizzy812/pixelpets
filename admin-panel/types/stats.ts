export interface DashboardStats {
  total_users: number;
  new_users_today: number;
  new_users_week: number;
  active_users_today: number;
  total_balance_xpet: string;
  pending_deposits_count: number;
  pending_deposits_amount: string;
  pending_withdrawals_count: number;
  pending_withdrawals_amount: string;
  total_deposited: string;
  total_withdrawn: string;
  total_pets_active: number;
  total_pets_evolved: number;
  total_claimed_xpet: string;
  total_ref_rewards_paid: string;
  total_task_rewards_paid: string;
}
