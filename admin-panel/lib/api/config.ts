import { apiClient } from "./client";
import {
  ConfigItem,
  ReferralConfig,
  UpdateConfigRequest,
  UpdateReferralConfigRequest,
} from "@/types";

export async function getConfigs(): Promise<ConfigItem[]> {
  const response = await apiClient.get<ConfigItem[]>("/admin/config");
  return response.data;
}

export async function getReferralConfig(): Promise<ReferralConfig> {
  const response = await apiClient.get<ReferralConfig>("/admin/config/referrals");
  return response.data;
}

export async function updateReferralConfig(
  data: UpdateReferralConfigRequest
): Promise<ReferralConfig> {
  const response = await apiClient.put<ReferralConfig>(
    "/admin/config/referrals",
    data
  );
  return response.data;
}

export async function updateConfig(
  key: string,
  data: UpdateConfigRequest
): Promise<ConfigItem> {
  const response = await apiClient.put<ConfigItem>(`/admin/config/${key}`, data);
  return response.data;
}
