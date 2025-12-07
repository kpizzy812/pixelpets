export type PetStatus =
  | 'EMPTY'
  | 'OWNED_IDLE'
  | 'TRAINING'
  | 'READY_TO_CLAIM'
  | 'EVOLVED'
  | 'SOLD';

export type PetLevel = 'BABY' | 'ADULT' | 'MYTHIC';

export type PetRarity = 'Common' | 'Uncommon' | 'Rare' | 'Epic' | 'Legendary' | 'Mythic';

export interface Pet {
  id: string;
  slotIndex: number;
  name: string;
  imageKey: string;
  level: PetLevel;
  rarity: PetRarity;
  invested: number;
  dailyRate: number;
  status: PetStatus;
  trainingEndsAt?: number;
  upgradeCost: number | null;    // Amount added to invested_total
  evolutionFee: number | null;   // 10% fee (not added to invested_total)
  profitClaimed: number;         // Total profit claimed so far
  roiCap: number;                // Max profit this pet can earn
  roiProgress: number;           // Progress to ROI cap (0-100)
}

export interface PetSlot {
  index: number;
  pet: Pet | null;
}
