'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useGameStore, useBalance, usePetSlots } from '@/store/game-store';
import { HeaderBalance } from './header-balance';
import { PetCarousel } from './pet-carousel';
import { BottomNav } from '@/components/layout/bottom-nav';
import { UpgradeModal, SellModal } from '@/components/pet';
import { showSuccess, showError, showPetAction } from '@/lib/toast';
import { formatNumber } from '@/lib/format';

export function HomeScreen() {
  const router = useRouter();
  const balance = useBalance();
  const petSlots = usePetSlots();
  const { startTraining, claimReward, fetchPets, user } = useGameStore();

  // Debug log
  console.log('[HomeScreen] petSlots:', petSlots, 'user:', user?.id, 'balance:', balance);

  // Modal states
  const [upgradeSlotIndex, setUpgradeSlotIndex] = useState<number | null>(null);
  const [sellSlotIndex, setSellSlotIndex] = useState<number | null>(null);

  const upgradePet = upgradeSlotIndex !== null ? petSlots[upgradeSlotIndex]?.pet : null;
  const sellPet = sellSlotIndex !== null ? petSlots[sellSlotIndex]?.pet : null;

  // Fetch pets on mount if we have a user
  useEffect(() => {
    if (user) {
      fetchPets();
    }
  }, [user, fetchPets]);

  const handleTrain = async (slotIndex: number) => {
    const slot = petSlots[slotIndex];
    if (slot?.pet) {
      try {
        await startTraining(Number(slot.pet.id));
        showPetAction(slot.pet.emoji, `${slot.pet.name} started training!`);
      } catch (err) {
        showError(err instanceof Error ? err.message : 'Failed to start training');
      }
    }
  };

  const handleClaim = async (slotIndex: number) => {
    const slot = petSlots[slotIndex];
    if (slot?.pet) {
      try {
        const result = await claimReward(Number(slot.pet.id));
        if (result.evolved) {
          showSuccess(`${slot.pet.name} evolved! +${formatNumber(result.profit)} XPET earned`);
        } else {
          showSuccess(`+${formatNumber(result.profit)} XPET claimed!`);
        }
      } catch (err) {
        showError(err instanceof Error ? err.message : 'Failed to claim reward');
      }
    }
  };

  const handleShop = () => {
    router.push('/shop');
  };

  const handleUpgrade = (slotIndex: number) => {
    setUpgradeSlotIndex(slotIndex);
  };

  const handleSell = (slotIndex: number) => {
    setSellSlotIndex(slotIndex);
  };

  // Get upgrade price from original API data (we need to track this)
  const getUpgradePrice = (slotIndex: number): number | null => {
    // For now return estimated upgrade price based on level
    const pet = petSlots[slotIndex]?.pet;
    if (!pet) return null;
    // Upgrade prices increase with level
    const basePrices: Record<number, number> = { 1: 25, 2: 50 };
    return basePrices[pet.level] ?? null;
  };

  return (
    <div className="h-screen flex flex-col bg-[#050712] overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#1a0a2e] via-[#0a0f1a] to-[#050712] pointer-events-none" />

      {/* Content */}
      <div className="relative flex flex-col h-full z-10">
        {/* Header */}
        <HeaderBalance balance={balance} />

        {/* Pet Carousel */}
        <PetCarousel
          slots={petSlots}
          onTrain={handleTrain}
          onClaim={handleClaim}
          onShop={handleShop}
          onUpgrade={handleUpgrade}
          onSell={handleSell}
        />

        {/* Bottom Navigation */}
        <BottomNav />
      </div>

      {/* Modals */}
      <UpgradeModal
        isOpen={upgradeSlotIndex !== null}
        onClose={() => setUpgradeSlotIndex(null)}
        pet={upgradePet}
        upgradePrice={upgradeSlotIndex !== null ? getUpgradePrice(upgradeSlotIndex) : null}
      />

      <SellModal
        isOpen={sellSlotIndex !== null}
        onClose={() => setSellSlotIndex(null)}
        pet={sellPet}
      />
    </div>
  );
}
