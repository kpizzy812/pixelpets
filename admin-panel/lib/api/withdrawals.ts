import { apiClient } from "./client";
import {
  WithdrawalsListResponse,
  WithdrawalsListParams,
  WithdrawalActionRequest,
  WithdrawalActionResponse,
} from "@/types";

export async function getWithdrawals(
  params?: WithdrawalsListParams
): Promise<WithdrawalsListResponse> {
  const response = await apiClient.get<WithdrawalsListResponse>("/admin/withdrawals", {
    params,
  });
  return response.data;
}

export async function withdrawalAction(
  withdrawalId: number,
  data: WithdrawalActionRequest
): Promise<WithdrawalActionResponse> {
  const response = await apiClient.post<WithdrawalActionResponse>(
    `/admin/withdrawals/${withdrawalId}/action`,
    data
  );
  return response.data;
}
