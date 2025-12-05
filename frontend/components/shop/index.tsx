'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageLayout } from '@/components/layout/page-layout';
import { PetTypeCard } from './pet-type-card';
import { BuyModal } from './buy-modal';
import { PetTypeCardSkeleton } from '@/components/ui/skeleton';
import { InlineError } from '@/components/ui/error-state';
import { useGameStore, useBalance } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import type { PetType } from '@/types/api';

export function ShopScreen() {
  const router = useRouter();
  const balance = useBalance();
  const { petTypes, petSlots, slotsUsed, maxSlots, fetchPetCatalog, buyPet, isLoading } = useGameStore();

  const [selectedPet, setSelectedPet] = useState<PetType | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const [isBuying, setIsBuying] = useState(false);

  useEffect(() => {
    fetchPetCatalog();
  }, [fetchPetCatalog]);

  const handleBuy = (petType: PetType) => {
    // Find first empty slot
    const emptySlot = petSlots.find((s) => s.pet === null);
    if (!emptySlot) {
      showError('No free slots available');
      return;
    }

    if (balance < petType.base_price) {
      showError('Not enough XPET');
      return;
    }

    setSelectedPet(petType);
    setSelectedSlot(emptySlot.index);
  };

  const handleConfirmBuy = async () => {
    if (!selectedPet || selectedSlot === null) return;

    setIsBuying(true);

    try {
      await buyPet(selectedPet.id, selectedSlot);
      showSuccess(`${selectedPet.name} purchased!`);
      setSelectedPet(null);
      setSelectedSlot(null);
      router.push('/');
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to buy pet');
    } finally {
      setIsBuying(false);
    }
  };

  const hasEmptySlots = slotsUsed < maxSlots;

  return (
    <PageLayout title="Pet Shop">
      <div className="p-4 space-y-4">
        {/* Slots Info */}
        <div className="p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex justify-between items-center">
          <span className="text-sm text-[#94a3b8]">Available Slots</span>
          <span className="text-sm font-medium text-[#f1f5f9]">
            {maxSlots - slotsUsed} / {maxSlots}
          </span>
        </div>

        {/* No Slots Warning */}
        {!hasEmptySlots && (
          <InlineError message="All pet slots are full. Sell or evolve a pet to buy a new one." />
        )}

        {/* Pet Catalog */}
        {isLoading && petTypes.length === 0 ? (
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <PetTypeCardSkeleton key={i} />
            ))}
          </div>
        ) : (
          petTypes.map((petType) => (
            <PetTypeCard
              key={petType.id}
              petType={petType}
              onBuy={() => handleBuy(petType)}
              disabled={!hasEmptySlots || balance < petType.base_price}
            />
          ))
        )}
      </div>

      {selectedPet && (
        <BuyModal
          petType={selectedPet}
          balance={balance}
          onConfirm={handleConfirmBuy}
          onClose={() => {
            setSelectedPet(null);
            setSelectedSlot(null);
          }}
          isLoading={isBuying}
        />
      )}
    </PageLayout>
  );
}
