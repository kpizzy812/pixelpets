'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import { useHaptic } from '@/hooks/use-haptic';
import { formatNumber } from '@/lib/format';
import type { Pet, PetLevel } from '@/types/pet';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  pet: Pet | null;
  upgradePrice: number | null;
}

const LEVEL_DISPLAY: Record<PetLevel, string> = {
  BABY: 'Baby',
  ADULT: 'Adult',
  MYTHIC: 'Mythic',
};

const NEXT_LEVEL: Record<PetLevel, PetLevel | null> = {
  BABY: 'ADULT',
  ADULT: 'MYTHIC',
  MYTHIC: null,
};

const LEVEL_BONUSES: Record<PetLevel, string> = {
  BABY: '',
  ADULT: '+0.2% daily rate',
  MYTHIC: '+0.4% daily rate',
};

export function UpgradeModal({ isOpen, onClose, pet, upgradePrice }: UpgradeModalProps) {
  const balance = useBalance();
  const { upgradePet } = useGameStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const { impact, success, error: hapticError, tap } = useHaptic();

  useEffect(() => {
    if (isOpen) {
      impact('light');
    }
  }, [isOpen, impact]);

  if (!isOpen || !pet) return null;

  const canAfford = upgradePrice !== null && balance >= upgradePrice;
  const isMaxLevel = pet.level === 'MYTHIC';
  const nextLevel = NEXT_LEVEL[pet.level];

  const handleClose = () => {
    tap();
    onClose();
  };

  const handleUpgrade = async () => {
    if (!canAfford || isMaxLevel || !nextLevel) return;

    setIsProcessing(true);

    try {
      await upgradePet(Number(pet.id));
      success();
      showSuccess(`${pet.name} upgraded to ${LEVEL_DISPLAY[nextLevel]}!`);
      onClose();
    } catch (err) {
      hapticError();
      showError(err instanceof Error ? err.message : 'Failed to upgrade pet');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isProcessing ? undefined : handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-[#c7f464]">Upgrade Pet</h2>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            ✕
          </button>
        </div>

        {isMaxLevel ? (
          <div className="p-4 rounded-xl bg-[#fbbf24]/10 border border-[#fbbf24]/30 mb-6 text-center">
            <span className="text-2xl mb-2 block">⭐</span>
            <p className="text-sm text-[#fbbf24]">This pet is already at maximum level!</p>
          </div>
        ) : nextLevel ? (
          <>
            {/* Evolution Preview */}
            <div className="p-5 rounded-2xl bg-[#1e293b]/40 mb-5">
              <div className="flex items-center justify-center gap-4">
                {/* Current Pet */}
                <div className="flex flex-col items-center">
                  <div className="rounded-2xl overflow-hidden bg-[#0d1220]/60 p-2">
                    <PetImage imageKey={pet.imageKey} level={pet.level} alt={pet.name} size={72} />
                  </div>
                  <span className="mt-2 px-3 py-1 rounded-lg bg-[#334155]/60 text-[#94a3b8] text-xs font-medium">
                    {LEVEL_DISPLAY[pet.level]}
                  </span>
                </div>

                {/* Arrow */}
                <div className="flex flex-col items-center gap-1">
                  <span className="text-2xl text-[#c7f464]">→</span>
                </div>

                {/* Next Level Pet */}
                <div className="flex flex-col items-center">
                  <div className="rounded-2xl overflow-hidden bg-[#c7f464]/10 p-2 ring-2 ring-[#c7f464]/30">
                    <PetImage imageKey={pet.imageKey} level={nextLevel} alt={pet.name} size={72} />
                  </div>
                  <span className="mt-2 px-3 py-1 rounded-lg bg-[#c7f464]/20 text-[#c7f464] text-xs font-medium">
                    {LEVEL_DISPLAY[nextLevel]}
                  </span>
                </div>
              </div>

              {/* Pet Name */}
              <h3 className="text-center text-lg font-bold text-[#f1f5f9] mt-4">{pet.name}</h3>
            </div>

            {/* Bonus Info */}
            <div className="p-4 rounded-xl bg-[#c7f464]/10 border border-[#c7f464]/20 mb-5">
              <div className="flex items-center justify-between">
                <span className="text-sm text-[#94a3b8]">Upgrade Bonus</span>
                <span className="text-sm text-[#c7f464] font-semibold">{LEVEL_BONUSES[nextLevel]}</span>
              </div>
            </div>

            {/* Price Info */}
            <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-6 space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-[#64748b]">Upgrade Cost</span>
                <span className="text-sm text-[#f1f5f9] font-medium inline-flex items-center gap-1">
                  {upgradePrice != null ? formatNumber(upgradePrice) : '---'} <XpetCoin size={18} />
                </span>
              </div>
              <div className="h-px bg-[#334155]" />
              <div className="flex justify-between items-center">
                <span className="text-sm text-[#64748b]">Your Balance</span>
                <span className={`text-sm font-medium inline-flex items-center gap-1 ${canAfford ? 'text-[#c7f464]' : 'text-red-400'}`}>
                  {formatNumber(balance)} <XpetCoin size={18} />
                </span>
              </div>
            </div>

            {/* Action Button */}
            <Button
              variant="lime"
              fullWidth
              onClick={handleUpgrade}
              disabled={isProcessing || !canAfford}
              haptic="heavy"
            >
              {isProcessing
                ? 'Upgrading...'
                : !canAfford
                ? 'Insufficient Balance'
                : `Upgrade for ${upgradePrice != null ? formatNumber(upgradePrice) : '---'} XPET`}
            </Button>
          </>
        ) : null}
      </div>
    </div>
  );
}
