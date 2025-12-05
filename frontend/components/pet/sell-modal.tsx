'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import { formatNumber } from '@/lib/format';
import type { Pet } from '@/types/pet';

interface SellModalProps {
  isOpen: boolean;
  onClose: () => void;
  pet: Pet | null;
}

const SELL_RATE = 0.7; // 70% refund

export function SellModal({ isOpen, onClose, pet }: SellModalProps) {
  const { sellPet } = useGameStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const [confirmText, setConfirmText] = useState('');

  if (!isOpen || !pet) return null;

  const refundAmount = pet.invested * SELL_RATE;
  const lossAmount = pet.invested - refundAmount;
  const isConfirmed = confirmText.toLowerCase() === 'sell';

  const handleSell = async () => {
    if (!isConfirmed) return;

    setIsProcessing(true);

    try {
      const refund = await sellPet(Number(pet.id));
      showSuccess(`${pet.name} sold! +${formatNumber(refund)} XPET refunded`);
      onClose();
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to sell pet');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isProcessing ? undefined : onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-red-400">Sell Pet</h2>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            X
          </button>
        </div>

        {/* Warning */}
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 mb-6 text-center">
          <span className="text-3xl mb-2 block">!!!</span>
          <p className="text-sm text-red-400 font-medium">This action cannot be undone!</p>
        </div>

        {/* Pet Info */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 mb-6 text-center">
          <div className="flex justify-center mb-3">
            <PetImage imageKey={pet.imageKey} alt={pet.name} size={80} />
          </div>
          <h3 className="text-lg font-bold text-[#f1f5f9]">{pet.name}</h3>
          <p className="text-sm text-[#64748b] mt-1">Level {pet.level}</p>
        </div>

        {/* Sell Info */}
        <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-6 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">Total Invested</span>
            <span className="text-sm text-[#f1f5f9] inline-flex items-center gap-1">{formatNumber(pet.invested)} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">Sell Rate</span>
            <span className="text-sm text-[#fbbf24]">{formatNumber(SELL_RATE * 100, 0)}%</span>
          </div>
          <div className="h-px bg-[#334155]" />
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">You Receive</span>
            <span className="text-sm text-[#c7f464] font-medium inline-flex items-center gap-1">{formatNumber(refundAmount)} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">Loss</span>
            <span className="text-sm text-red-400 inline-flex items-center gap-1">-{formatNumber(lossAmount)} <XpetCoin size={18} /></span>
          </div>
        </div>

        {/* Confirmation Input */}
        <div className="mb-6">
          <label className="text-xs text-[#64748b] uppercase tracking-wide mb-2 block">
            Type &quot;SELL&quot; to confirm
          </label>
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            placeholder="SELL"
            className="w-full p-4 rounded-xl bg-[#1e293b]/40 border border-[#334155]/50 text-[#f1f5f9] placeholder-[#64748b] focus:outline-none focus:border-red-500/50 uppercase"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button
            variant="ghost"
            fullWidth
            onClick={onClose}
            disabled={isProcessing}
          >
            Cancel
          </Button>
          <button
            onClick={handleSell}
            disabled={isProcessing || !isConfirmed}
            className={`flex-1 py-3 rounded-xl font-medium transition-all ${
              isConfirmed && !isProcessing
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-[#1e293b]/60 text-[#64748b] cursor-not-allowed'
            }`}
          >
            {isProcessing ? 'Selling...' : 'Sell Pet'}
          </button>
        </div>
      </div>
    </div>
  );
}
