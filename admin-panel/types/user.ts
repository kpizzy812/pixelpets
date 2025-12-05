export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language_code: string;
  balance_xpet: string;
  ref_code: string;
  referrer_id: number | null;
  ref_levels_unlocked: number;
  created_at: string;
  updated_at: string;
  total_deposited: string;
  total_withdrawn: string;
  total_claimed: string;
  total_ref_earned: string;
  active_pets_count: number;
  referrals_count: number;
}

export interface UsersListResponse {
  users: User[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface UsersListParams {
  page?: number;
  per_page?: number;
  search?: string;
  order_by?: string;
  order_desc?: boolean;
}

export interface BalanceAdjustRequest {
  amount: number;
  reason: string;
}

export interface BalanceAdjustResponse {
  user_id: number;
  old_balance: string;
  new_balance: string;
  amount: string;
  reason: string;
  transaction_id: number;
}
