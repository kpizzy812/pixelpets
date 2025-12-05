'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import { useHaptic } from '@/hooks/use-haptic';
import { formatNumber } from '@/lib/format';
import type { Pet } from '@/types/pet';

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  pet: Pet | null;
  upgradePrice: number | null;
}

const LEVEL_NAMES: Record<number, string> = {
  1: 'Baby',
  2: 'Adult',
  3: 'Mythic',
};

const LEVEL_BONUSES: Record<number, string> = {
  2: '+0.2% daily rate',
  3: '+0.4% daily rate',
};

export function UpgradeModal({ isOpen, onClose, pet, upgradePrice }: UpgradeModalProps) {
  const balance = useBalance();
  const { upgradePet } = useGameStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const { impact, success, error: hapticError, tap } = useHaptic();

  // Haptic on modal open
  useEffect(() => {
    if (isOpen) {
      impact('light');
    }
  }, [isOpen, impact]);

  if (!isOpen || !pet) return null;

  const canAfford = upgradePrice !== null && balance >= upgradePrice;
  const isMaxLevel = pet.level >= 3;
  const nextLevel = pet.level + 1;

  const handleClose = () => {
    tap();
    onClose();
  };

  const handleUpgrade = async () => {
    if (!canAfford || isMaxLevel) return;

    setIsProcessing(true);

    try {
      await upgradePet(Number(pet.id));
      success();
      showSuccess(`${pet.name} upgraded to ${LEVEL_NAMES[nextLevel]}!`);
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
          <h2 className="text-xl font-bold text-[#f1f5f9]">Upgrade Pet</h2>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            X
          </button>
        </div>

        {/* Pet Info */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 mb-6 text-center">
          <div className="flex justify-center mb-3">
            <PetImage imageKey={pet.imageKey} alt={pet.name} size={80} />
          </div>
          <h3 className="text-lg font-bold text-[#f1f5f9]">{pet.name}</h3>
          <div className="flex justify-center items-center gap-2 mt-2">
            <span className="px-3 py-1 rounded-lg bg-[#00f5d4]/20 text-[#00f5d4] text-sm">
              {LEVEL_NAMES[pet.level]} (Lvl {pet.level})
            </span>
          </div>
        </div>

        {isMaxLevel ? (
          <div className="p-4 rounded-xl bg-[#fbbf24]/10 border border-[#fbbf24]/30 mb-6 text-center">
            <span className="text-2xl mb-2 block">*</span>
            <p className="text-sm text-[#fbbf24]">This pet is already at maximum level!</p>
          </div>
        ) : (
          <>
            {/* Upgrade Preview */}
            <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-6">
              <div className="flex justify-between items-center mb-3">
                <span className="text-sm text-[#64748b]">Current Level</span>
                <span className="text-sm text-[#f1f5f9]">{LEVEL_NAMES[pet.level]}</span>
              </div>
              <div className="flex justify-center mb-3">
                <span className="text-[#c7f464] text-xl">-&gt;</span>
              </div>
              <div className="flex justify-between items-center mb-3">
                <span className="text-sm text-[#64748b]">New Level</span>
                <span className="text-sm text-[#c7f464] font-medium">{LEVEL_NAMES[nextLevel]}</span>
              </div>
              <div className="h-px bg-[#334155] my-3" />
              <div className="flex justify-between items-center">
                <span className="text-sm text-[#64748b]">Bonus</span>
                <span className="text-sm text-[#c7f464]">{LEVEL_BONUSES[nextLevel]}</span>
              </div>
            </div>

            {/* Price Info */}
            <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-[#64748b]">Upgrade Cost</span>
                <span className="text-sm text-[#f1f5f9] font-medium inline-flex items-center gap-1">
                  {upgradePrice != null ? formatNumber(upgradePrice) : '---'} <XpetCoin size={14} />
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-[#64748b]">Your Balance</span>
                <span className={`text-sm font-medium inline-flex items-center gap-1 ${canAfford ? 'text-[#c7f464]' : 'text-red-400'}`}>
                  {formatNumber(balance)} <XpetCoin size={14} />
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
        )}
      </div>
    </div>
  );
}
