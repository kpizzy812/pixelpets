/**
 * API Types - mirrors backend schemas
 */

// Enums
export type PetStatus = 'OWNED_IDLE' | 'TRAINING' | 'READY_TO_CLAIM' | 'EVOLVED' | 'SOLD';
export type PetLevel = 'BABY' | 'TEEN' | 'ADULT';
// Backend TxType values (lowercase)
export type TxType = 'deposit' | 'withdraw' | 'claim' | 'ref_reward' | 'task_reward' | 'sell_refund' | 'admin_adjust' | 'pet_buy' | 'pet_upgrade';
export type NetworkType = 'BEP-20' | 'Solana' | 'TON';
export type RequestStatus = 'PENDING' | 'COMPLETED' | 'REJECTED' | 'EXPIRED';

// Auth
export interface User {
  id: number;
  telegram_id: number;
  username: string | null;
  first_name: string | null;
  last_name: string | null;
  language_code: string;
  balance_xpet: number;
  ref_code: string;
  referrer_id: number | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Pet Types (catalog)
export interface PetType {
  id: number;
  name: string;
  emoji: string;
  image_key: string;
  base_price: number;
  daily_rate: number;
  roi_cap_multiplier: number;
  level_prices: Record<string, number>;
  is_active: boolean;
}

// User Pet
export interface UserPet {
  id: number;
  pet_type: PetType;
  slot_index: number;
  level: PetLevel;
  status: PetStatus;
  invested_total: number;
  profit_claimed: number;
  training_started_at: string | null;
  training_ends_at: string | null;
  current_daily_rate: number;
  roi_cap: number;
  roi_progress: number;
  can_claim: boolean;
  claimable_amount: number;
  upgrade_price: number | null;
}

export interface MyPetsResponse {
  pets: UserPet[];
  slots_used: number;
  max_slots: number;
}

export interface ClaimResponse {
  profit: number;
  new_balance: number;
  evolved: boolean;
}

export interface HallOfFameEntry {
  id: number;
  pet_type: PetType;
  final_level: PetLevel;
  invested_total: number;
  total_farmed: number;
  lifetime_days: number;
  evolved_at: string;
}

export interface HallOfFameResponse {
  pets: HallOfFameEntry[];
  total_pets_evolved: number;
  total_farmed_all_time: number;
}

// Wallet
export interface WalletResponse {
  balance_xpet: number;
  balance_usd: number;
  pending_deposits: number;
  pending_withdrawals: number;
}

export interface DepositRequestResponse {
  request_id: number;
  amount: number;
  network: NetworkType;
  deposit_address: string | null;
  status: RequestStatus;
  created_at: string;
}

export interface WithdrawRequestResponse {
  request_id: number;
  amount: number;
  fee: number;
  total_deducted: number;
  network: NetworkType;
  wallet_address: string;
  status: RequestStatus;
  new_balance: number;
}

export interface Transaction {
  id: number;
  type: TxType;
  amount_xpet: number;
  fee: number;
  meta: Record<string, unknown> | null;
  created_at: string;
}

export interface TransactionsResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  pages: number;
}

// Referrals
export interface RefLevelStats {
  level: number;
  percentage: number;
  count: number;
  earned: number;
  unlocked: boolean;
}

export interface ReferralsResponse {
  ref_code: string;
  ref_link: string;
  total_referrals: number;
  active_referrals: number;
  total_earned: number;
  levels: RefLevelStats[];
}

// Tasks
export interface Task {
  id: number;
  title: string;
  description: string | null;
  reward_xpet: number;
  link: string | null;
  task_type: string;
  is_completed: boolean;
}

export interface TasksResponse {
  tasks: Task[];
  completed_count: number;
  total_count: number;
}

export interface TaskCheckResponse {
  success: boolean;
  reward: number;
  new_balance: number;
}
