'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageLayout } from '@/components/layout/page-layout';
import { PetTypeCard } from './pet-type-card';
import { BuyModal } from './buy-modal';
import { SellModal } from '@/components/pet/sell-modal';
import { PetTypeCardSkeleton } from '@/components/ui/skeleton';
import { InlineError } from '@/components/ui/error-state';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import { formatNumber } from '@/lib/format';
import type { PetType } from '@/types/api';
import type { Pet } from '@/types/pet';

type ShopMode = 'buy' | 'sell';

export function ShopScreen() {
  const router = useRouter();
  const balance = useBalance();
  const { petTypes, petSlots, slotsUsed, maxSlots, fetchPetCatalog, buyPet, isLoading } = useGameStore();

  const [mode, setMode] = useState<ShopMode>('buy');
  const [selectedPet, setSelectedPet] = useState<PetType | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const [isBuying, setIsBuying] = useState(false);
  const [sellPet, setSellPet] = useState<Pet | null>(null);

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
        {/* Buy/Sell Toggle */}
        <div className="flex rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 p-1">
          <button
            onClick={() => setMode('buy')}
            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
              mode === 'buy'
                ? 'bg-[#c7f464] text-[#0d1220]'
                : 'text-[#94a3b8] hover:text-[#f1f5f9]'
            }`}
          >
            Buy
          </button>
          <button
            onClick={() => setMode('sell')}
            className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
              mode === 'sell'
                ? 'bg-[#c7f464] text-[#0d1220]'
                : 'text-[#94a3b8] hover:text-[#f1f5f9]'
            }`}
          >
            Sell
          </button>
        </div>

        {mode === 'buy' ? (
          <>
            {/* No Slots Warning */}
            {!hasEmptySlots && (
              <InlineError message="All pet slots are full. Sell or evolve a pet to buy a new one." />
            )}

            {/* Pet Catalog - Grid 2x2 */}
            {isLoading && petTypes.length === 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <PetTypeCardSkeleton key={i} />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                {petTypes.map((petType) => (
                  <PetTypeCard
                    key={petType.id}
                    petType={petType}
                    onBuy={() => handleBuy(petType)}
                    disabled={!hasEmptySlots || balance < petType.base_price}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <>
            {/* User's Pets for Sale */}
            {(() => {
              const ownedPets = petSlots.filter(slot => slot.pet !== null);
              if (ownedPets.length === 0) {
                return (
                  <div className="text-center py-12 text-[#64748b]">
                    <p className="text-sm">You don't have any pets to sell</p>
                  </div>
                );
              }
              return (
                <div className="space-y-3">
                  {ownedPets.map((slot) => {
                    const pet = slot.pet!;
                    const refundAmount = pet.invested * 0.7;
                    return (
                      <div
                        key={slot.index}
                        className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50"
                      >
                        <div className="flex items-center gap-4">
                          {/* Pet Image */}
                          <div className="w-16 h-16 rounded-xl bg-[#1e293b]/40 overflow-hidden flex-shrink-0">
                            <PetImage imageKey={pet.imageKey} alt={pet.name} size={64} className="w-full h-full object-cover" />
                          </div>

                          {/* Pet Info */}
                          <div className="flex-1 min-w-0">
                            <h3 className="text-base font-semibold text-[#f1f5f9] truncate">{pet.name}</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-[#64748b]">Lvl {pet.level}</span>
                              <span className="text-xs text-[#64748b]">•</span>
                              <span className="text-xs text-[#94a3b8]">{pet.rarity}</span>
                            </div>
                            <div className="flex items-center gap-1 mt-1">
                              <span className="text-xs text-[#64748b]">Refund:</span>
                              <span className="text-xs text-[#c7f464] font-medium">{formatNumber(refundAmount)}</span>
                              <XpetCoin size={12} />
                            </div>
                          </div>

                          {/* Sell Button */}
                          <button
                            onClick={() => setSellPet(pet)}
                            className="px-4 py-2 rounded-xl bg-red-500/20 border border-red-500/40 text-red-400 text-sm font-medium hover:bg-red-500/30 transition-colors"
                          >
                            Sell
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })()}
          </>
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

      <SellModal
        isOpen={sellPet !== null}
        onClose={() => setSellPet(null)}
        pet={sellPet}
      />
    </PageLayout>
  );
}
