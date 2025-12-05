import { apiClient } from "./client";
import { LogsListResponse, LogsListParams } from "@/types";

export async function getLogs(params?: LogsListParams): Promise<LogsListResponse> {
  const response = await apiClient.get<LogsListResponse>("/admin/logs", { params });
  return response.data;
}
