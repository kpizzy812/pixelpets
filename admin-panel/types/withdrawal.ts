import { NetworkType } from "./deposit";

export type WithdrawalStatus = "PENDING" | "COMPLETED" | "REJECTED";

export interface Withdrawal {
  id: number;
  user_id: number;
  telegram_id: number;
  username: string | null;
  amount: string;
  fee: string;
  net_amount: string;
  network: NetworkType;
  wallet_address: string;
  status: WithdrawalStatus;
  created_at: string;
  processed_at: string | null;
  processed_by: number | null;
}

export interface WithdrawalsListResponse {
  withdrawals: Withdrawal[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface WithdrawalsListParams {
  page?: number;
  per_page?: number;
  status?: WithdrawalStatus;
  network?: NetworkType;
  user_id?: number;
}

export interface WithdrawalActionRequest {
  action: "complete" | "reject";
  tx_hash?: string;
  note?: string;
}

export interface WithdrawalActionResponse {
  status: string;
  withdrawal_id: number;
  new_status: WithdrawalStatus;
}
