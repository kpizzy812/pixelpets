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
}

export interface PetSlot {
  index: number;
  pet: Pet | null;
}
