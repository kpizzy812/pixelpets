import { apiClient } from "./client";
import {
  DepositsListResponse,
  DepositsListParams,
  DepositActionRequest,
  DepositActionResponse,
} from "@/types";

export async function getDeposits(
  params?: DepositsListParams
): Promise<DepositsListResponse> {
  const response = await apiClient.get<DepositsListResponse>("/admin/deposits", {
    params,
  });
  return response.data;
}

export async function depositAction(
  depositId: number,
  data: DepositActionRequest
): Promise<DepositActionResponse> {
  const response = await apiClient.post<DepositActionResponse>(
    `/admin/deposits/${depositId}/action`,
    data
  );
  return response.data;
}
