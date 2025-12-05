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
  WalletResponse,
  DepositRequestResponse,
  WithdrawRequestResponse,
  TransactionsResponse,
  ReferralsResponse,
  TasksResponse,
  TaskCheckResponse,
  NetworkType,
  TxType,
} from '@/types/api';

// Auth
export const authApi = {
  loginTelegram: (initData: string) =>
    api.post<AuthResponse>('/auth/telegram', { init_data: initData }),

  me: () => api.get<User>('/auth/me'),
};

// Pets
export const petsApi = {
  catalog: () => api.get<{ pets: PetType[] }>('/pets/catalog').then(res => res.pets),

  my: () => api.get<MyPetsResponse>('/pets/my'),

  buy: (petTypeId: number, slotIndex: number) =>
    api.post<UserPet>('/pets/buy', { pet_type_id: petTypeId, slot_index: slotIndex }),

  upgrade: (petId: number) =>
    api.post<UserPet>(`/pets/${petId}/upgrade`),

  sell: (petId: number) =>
    api.post<{ refund: number; new_balance: number }>(`/pets/${petId}/sell`),

  startTraining: (petId: number) =>
    api.post<UserPet>(`/pets/${petId}/start-training`),

  claim: (petId: number) =>
    api.post<ClaimResponse>(`/pets/${petId}/claim`),

  hallOfFame: () =>
    api.get<UserPet[]>('/pets/hall-of-fame'),
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
    api.post<TaskCheckResponse>(`/tasks/${taskId}/check`),
};
