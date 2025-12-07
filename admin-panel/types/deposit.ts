export type DepositStatus = "PENDING" | "APPROVED" | "REJECTED";
export type NetworkType = "BEP-20" | "Solana" | "TON";

export interface Deposit {
  id: number;
  user_id: number;
  telegram_id: number;
  username: string | null;
  amount: string;
  network: NetworkType;
  deposit_address: string | null;
  status: DepositStatus;
  created_at: string;
  confirmed_at: string | null;
  confirmed_by: number | null;
}

export interface DepositsListResponse {
  deposits: Deposit[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface DepositsListParams {
  page?: number;
  per_page?: number;
  status?: DepositStatus;
  network?: NetworkType;
  user_id?: number;
}

export interface DepositActionRequest {
  action: "approve" | "reject";
  note?: string;
}

export interface DepositActionResponse {
  status: string;
  deposit_id: number;
  new_status: DepositStatus;
}
