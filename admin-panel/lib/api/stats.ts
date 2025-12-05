import { apiClient } from "./client";
import { DashboardStats } from "@/types";

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>("/admin/stats/dashboard");
  return response.data;
}
