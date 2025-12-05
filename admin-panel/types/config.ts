export interface ConfigItem {
  id: number;
  key: string;
  value: unknown;
  description: string | null;
  updated_at: string;
}

export interface ReferralConfig {
  percentages: Record<string, number>;
  unlock_thresholds: Record<string, number>;
}

export interface UpdateConfigRequest {
  value: unknown;
  description?: string | null;
}

export interface UpdateReferralConfigRequest {
  percentages?: Record<string, number> | null;
  unlock_thresholds?: Record<string, number> | null;
}
