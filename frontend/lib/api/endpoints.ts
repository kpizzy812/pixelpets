/**
 * Typed API endpoints
 */

import { api } from './client';
import type {
  AuthResponse,
  User,
  PetType,
  MyPetsResponse,
  UserPet,
  ClaimResponse,
  HallOfFameResponse,
  WalletResponse,
  DepositRequestResponse,
  WithdrawRequestResponse,
  TransactionsResponse,
  ReferralsResponse,
  TasksResponse,
  TaskCheckResponse,
  SpinWheelResponse,
  SpinResultResponse,
  NetworkType,
  TxType,
  PetStatus,
  SnackType,
  SnackPricesResponse,
  BuySnackResponse,
  RoiBoostPricesResponse,
  BuyRoiBoostResponse,
  AutoClaimStatusResponse,
  BuyAutoClaimResponse,
  BoostStatsResponse,
} from '@/types/api';

// Auth
export const authApi = {
  loginTelegram: (initData: string, refCode?: string | null) =>
    api.post<AuthResponse>('/auth/telegram', {
      init_data: initData,
      ...(refCode && { ref_code: refCode }),
    }),

  me: () => api.get<User>('/auth/me'),
};

// Pets
export const petsApi = {
  catalog: () => api.get<{ pets: PetType[] }>('/pets/catalog').then(res => res.pets),

  my: () => api.get<MyPetsResponse>('/pets/my'),

  buy: (petTypeId: number, slotIndex: number) =>
    api.post<{ pet: UserPet; new_balance: number }>('/pets/buy', { pet_type_id: petTypeId, slot_index: slotIndex }),

  upgrade: (petId: number) =>
    api.post<{ pet: UserPet; new_balance: number }>('/pets/upgrade', { pet_id: petId }),

  sell: (petId: number) =>
    api.post<{ refund_amount: number; new_balance: number }>('/pets/sell', { pet_id: petId }),

  startTraining: (petId: number) =>
    api.post<{ pet_id: number; status: PetStatus; training_started_at: string; training_ends_at: string }>('/pets/start-training', { pet_id: petId }),

  claim: (petId: number) =>
    api.post<ClaimResponse>('/pets/claim', { pet_id: petId }),

  hallOfFame: () =>
    api.get<HallOfFameResponse>('/pets/hall-of-fame'),
};

// Wallet
export const walletApi = {
  info: () => api.get<WalletResponse>('/wallet'),

  createDeposit: (network: NetworkType, amount: number) =>
    api.post<DepositRequestResponse>('/wallet/deposit-request', {
      network,
      amount,
    }),

  createWithdraw: (network: NetworkType, walletAddress: string, amount: number) =>
    api.post<WithdrawRequestResponse>('/wallet/withdraw-request', {
      network,
      wallet_address: walletAddress,
      amount,
    }),

  transactions: (page = 1, limit = 20, txType?: TxType) => {
    const params = new URLSearchParams({
      page: String(page),
      limit: String(limit),
    });
    if (txType) params.set('type', txType);
    return api.get<TransactionsResponse>(`/wallet/transactions?${params}`);
  },
};

// Referrals
export const referralsApi = {
  stats: () => api.get<ReferralsResponse>('/referrals'),

  link: () => api.get<{ ref_link: string }>('/referrals/link'),
};

// Tasks
export const tasksApi = {
  list: () => api.get<TasksResponse>('/tasks'),

  check: (taskId: number) =>
    api.post<TaskCheckResponse>('/tasks/check', { task_id: taskId }),
};

// Spin
export const spinApi = {
  wheel: () => api.get<SpinWheelResponse>('/spin/wheel'),

  spin: (isFree: boolean) =>
    api.post<SpinResultResponse>('/spin/spin', { is_free: isFree }),
};

// Boosts
export const boostsApi = {
  // Snacks
  snackPrices: (petId: number) =>
    api.get<SnackPricesResponse>(`/boosts/snacks/prices/${petId}`),

  buySnack: (petId: number, snackType: SnackType) =>
    api.post<BuySnackResponse>('/boosts/snacks/buy', { pet_id: petId, snack_type: snackType }),

  // ROI Boosts
  roiPrices: (petId: number) =>
    api.get<RoiBoostPricesResponse>(`/boosts/roi/prices/${petId}`),

  buyRoiBoost: (petId: number, boostPercent: number) =>
    api.post<BuyRoiBoostResponse>('/boosts/roi/buy', { pet_id: petId, boost_percent: boostPercent }),

  // Auto-Claim
  autoClaimStatus: () =>
    api.get<AutoClaimStatusResponse>('/boosts/auto-claim/status'),

  buyAutoClaim: (months: number) =>
    api.post<BuyAutoClaimResponse>('/boosts/auto-claim/buy', { months }),

  // Stats
  stats: () => api.get<BoostStatsResponse>('/boosts/stats'),
};
