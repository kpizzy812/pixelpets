export interface LevelPrices {
  BABY: number;
  ADULT: number;
  MYTHIC: number;
}

export interface PetType {
  id: number;
  name: string;
  emoji: string | null;
  base_price: string;
  daily_rate: string;
  roi_cap_multiplier: string;
  level_prices: LevelPrices;
  is_active: boolean;
  created_at: string;
}

export interface CreatePetTypeRequest {
  name: string;
  emoji?: string | null;
  base_price: number;
  daily_rate: number;
  roi_cap_multiplier: number;
  level_prices: LevelPrices;
  is_active?: boolean;
}

export interface UpdatePetTypeRequest {
  name?: string | null;
  emoji?: string | null;
  base_price?: number | null;
  daily_rate?: number | null;
  roi_cap_multiplier?: number | null;
  level_prices?: Partial<LevelPrices> | null;
  is_active?: boolean | null;
}

export interface DeletePetTypeResponse {
  status: string;
  deleted: number;
}
