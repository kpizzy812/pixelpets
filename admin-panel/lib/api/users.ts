import { apiClient } from "./client";
import {
  User,
  UsersListResponse,
  UsersListParams,
  BalanceAdjustRequest,
  BalanceAdjustResponse,
} from "@/types";

export async function getUsers(params?: UsersListParams): Promise<UsersListResponse> {
  const response = await apiClient.get<UsersListResponse>("/admin/users", { params });
  return response.data;
}

export async function getUser(userId: number): Promise<User> {
  const response = await apiClient.get<User>(`/admin/users/${userId}`);
  return response.data;
}

export async function adjustBalance(
  userId: number,
  data: BalanceAdjustRequest
): Promise<BalanceAdjustResponse> {
  const response = await apiClient.post<BalanceAdjustResponse>(
    `/admin/users/${userId}/balance`,
    data
  );
  return response.data;
}
