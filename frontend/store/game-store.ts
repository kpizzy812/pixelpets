import { create } from 'zustand';
import type { User, PetType, UserPet, MyPetsResponse, Task, ReferralsResponse } from '@/types/api';
import type { PetSlot, Pet } from '@/types/pet';
import { authApi, petsApi, tasksApi, referralsApi } from '@/lib/api';

// Convert API UserPet to frontend Pet format
function mapUserPetToPet(userPet: UserPet): Pet {
  const getRarity = (price: number): Pet['rarity'] => {
    if (price >= 300) return 'Legendary';
    if (price >= 150) return 'Epic';
    if (price >= 100) return 'Rare';
    if (price >= 50) return 'Uncommon';
    return 'Common';
  };

  return {
    id: String(userPet.id),
    slotIndex: userPet.slot_index,
    name: userPet.pet_type.name,
    imageKey: userPet.pet_type.image_key,
    level: userPet.level === 'BABY' ? 1 : userPet.level === 'ADULT' ? 2 : 3,
    rarity: getRarity(userPet.pet_type.base_price),
    invested: userPet.invested_total,
    dailyRate: userPet.current_daily_rate,
    status: userPet.status,
    trainingEndsAt: userPet.training_ends_at
      ? new Date(userPet.training_ends_at).getTime()
      : undefined,
  };
}

// Build pet slots array from API response
function buildPetSlots(pets: UserPet[], maxSlots: number): PetSlot[] {
  const slots: PetSlot[] = [];
  for (let i = 0; i < maxSlots; i++) {
    const pet = pets.find((p) => p.slot_index === i);
    slots.push({
      index: i,
      pet: pet ? mapUserPetToPet(pet) : null,
    });
  }
  return slots;
}

// State types
interface GameState {
  // User
  user: User | null;
  isLoading: boolean;
  error: string | null;

  // Pets
  petSlots: PetSlot[];
  petTypes: PetType[];
  slotsUsed: number;
  maxSlots: number;

  // Tasks
  tasks: Task[];
  tasksLoading: boolean;

  // Referrals
  referrals: ReferralsResponse | null;
  referralsLoading: boolean;
}

interface GameActions {
  // User
  setUser: (user: User | null) => void;
  updateBalance: (balance: number) => void;

  // Pets
  fetchPets: () => Promise<void>;
  fetchPetCatalog: () => Promise<void>;
  buyPet: (petTypeId: number, slotIndex: number) => Promise<void>;
  startTraining: (petId: number) => Promise<void>;
  claimReward: (petId: number) => Promise<{ profit: number; evolved: boolean }>;
  upgradePet: (petId: number) => Promise<void>;
  sellPet: (petId: number) => Promise<number>;

  // Tasks
  fetchTasks: () => Promise<void>;
  checkTask: (taskId: number) => Promise<{ success: boolean; reward: number }>;

  // Referrals
  fetchReferrals: () => Promise<void>;

  // Utils
  reset: () => void;
}

type GameStore = GameState & GameActions;

// Initial state
const initialState: GameState = {
  user: null,
  isLoading: false,
  error: null,
  petSlots: [
    { index: 0, pet: null },
    { index: 1, pet: null },
    { index: 2, pet: null },
  ],
  petTypes: [],
  slotsUsed: 0,
  maxSlots: 3,
  tasks: [],
  tasksLoading: false,
  referrals: null,
  referralsLoading: false,
};

export const useGameStore = create<GameStore>()((set, get) => ({
  ...initialState,

  // User actions
  setUser: (user) => set({ user }),

  updateBalance: (balance) =>
    set((state) => ({
      user: state.user ? { ...state.user, balance_xpet: balance } : null,
    })),

  // Pet actions
  fetchPets: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await petsApi.my();
      set({
        petSlots: buildPetSlots(response.pets, response.max_slots),
        slotsUsed: response.slots_used,
        maxSlots: response.max_slots,
        isLoading: false,
      });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to fetch pets',
        isLoading: false,
      });
    }
  },

  fetchPetCatalog: async () => {
    try {
      const petTypes = await petsApi.catalog();
      set({ petTypes });
    } catch (err) {
      console.error('Failed to fetch pet catalog:', err);
    }
  },

  buyPet: async (petTypeId, slotIndex) => {
    set({ isLoading: true, error: null });
    try {
      const newPet = await petsApi.buy(petTypeId, slotIndex);
      // Refresh user balance
      const userData = await authApi.me();
      set((state) => ({
        petSlots: state.petSlots.map((slot) =>
          slot.index === slotIndex
            ? { ...slot, pet: mapUserPetToPet(newPet) }
            : slot
        ),
        slotsUsed: state.slotsUsed + 1,
        user: userData,
        isLoading: false,
      }));
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to buy pet',
        isLoading: false,
      });
      throw err;
    }
  },

  startTraining: async (petId) => {
    try {
      const updatedPet = await petsApi.startTraining(petId);
      set((state) => ({
        petSlots: state.petSlots.map((slot) =>
          slot.pet && Number(slot.pet.id) === petId
            ? { ...slot, pet: mapUserPetToPet(updatedPet) }
            : slot
        ),
      }));
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to start training' });
      throw err;
    }
  },

  claimReward: async (petId) => {
    try {
      const result = await petsApi.claim(petId);
      set((state) => {
        const newSlots = state.petSlots.map((slot) => {
          if (slot.pet && Number(slot.pet.id) === petId) {
            if (result.evolved) {
              return { ...slot, pet: null };
            }
            return {
              ...slot,
              pet: {
                ...slot.pet,
                status: 'OWNED_IDLE' as const,
                trainingEndsAt: undefined,
              },
            };
          }
          return slot;
        });

        return {
          petSlots: newSlots,
          slotsUsed: result.evolved ? state.slotsUsed - 1 : state.slotsUsed,
          user: state.user
            ? { ...state.user, balance_xpet: result.new_balance }
            : null,
        };
      });
      return { profit: result.profit, evolved: result.evolved };
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to claim reward' });
      throw err;
    }
  },

  upgradePet: async (petId) => {
    try {
      const updatedPet = await petsApi.upgrade(petId);
      const userData = await authApi.me();
      set((state) => ({
        petSlots: state.petSlots.map((slot) =>
          slot.pet && Number(slot.pet.id) === petId
            ? { ...slot, pet: mapUserPetToPet(updatedPet) }
            : slot
        ),
        user: userData,
      }));
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to upgrade pet' });
      throw err;
    }
  },

  sellPet: async (petId) => {
    try {
      const result = await petsApi.sell(petId);
      set((state) => ({
        petSlots: state.petSlots.map((slot) =>
          slot.pet && Number(slot.pet.id) === petId ? { ...slot, pet: null } : slot
        ),
        slotsUsed: state.slotsUsed - 1,
        user: state.user
          ? { ...state.user, balance_xpet: result.new_balance }
          : null,
      }));
      return result.refund;
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Failed to sell pet' });
      throw err;
    }
  },

  // Task actions
  fetchTasks: async () => {
    set({ tasksLoading: true });
    try {
      const response = await tasksApi.list();
      set({ tasks: response.tasks, tasksLoading: false });
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      set({ tasksLoading: false });
    }
  },

  checkTask: async (taskId) => {
    try {
      const result = await tasksApi.check(taskId);
      if (result.success) {
        set((state) => ({
          tasks: state.tasks.map((t) =>
            t.id === taskId ? { ...t, is_completed: true } : t
          ),
          user: state.user
            ? { ...state.user, balance_xpet: result.new_balance }
            : null,
        }));
      }
      return { success: result.success, reward: result.reward };
    } catch (err) {
      console.error('Failed to check task:', err);
      throw err;
    }
  },

  // Referral actions
  fetchReferrals: async () => {
    set({ referralsLoading: true });
    try {
      const referrals = await referralsApi.stats();
      set({ referrals, referralsLoading: false });
    } catch (err) {
      console.error('Failed to fetch referrals:', err);
      set({ referralsLoading: false });
    }
  },

  // Utils
  reset: () => set(initialState),
}));

// Selectors
export const useBalance = () =>
  useGameStore((state) => state.user?.balance_xpet ?? 0);

export const usePetSlots = () => useGameStore((state) => state.petSlots);

export const useIsLoading = () => useGameStore((state) => state.isLoading);
