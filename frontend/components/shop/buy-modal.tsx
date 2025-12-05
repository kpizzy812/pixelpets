'use client';

import { useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useHaptic } from '@/hooks/use-haptic';
import type { PetType } from '@/types/api';

interface BuyModalProps {
  petType: PetType;
  balance: number;
  onConfirm: () => void;
  onClose: () => void;
  isLoading?: boolean;
}

export function BuyModal({ petType, balance, onConfirm, onClose, isLoading }: BuyModalProps) {
  const { impact, tap } = useHaptic();
  const maxProfit = petType.base_price * petType.roi_cap_multiplier;
  const netProfit = maxProfit - petType.base_price;
  const newBalance = balance - petType.base_price;
  const canAfford = balance >= petType.base_price;

  // Haptic on modal open
  useEffect(() => {
    impact('light');
  }, [impact]);

  const handleClose = () => {
    tap();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isLoading ? undefined : handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl">
        {/* Pet Preview */}
        <div className="text-center mb-6">
          <div className="w-24 h-24 mx-auto rounded-2xl bg-gradient-to-br from-[#1e293b]/80 to-[#0f172a]/80 border border-[#334155]/30 flex items-center justify-center mb-4">
            <span className="text-6xl">{petType.emoji}</span>
          </div>
          <h2 className="text-xl font-bold text-[#f1f5f9]">{petType.name}</h2>
          <p className="text-sm text-[#64748b] mt-1">Confirm recruitment</p>
        </div>

        {/* Stats */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Price</span>
            <span className="text-[#f1f5f9] font-medium">{petType.base_price} XPET</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Daily Rate</span>
            <span className="text-[#c7f464] font-medium">+{petType.daily_rate}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">ROI Cap</span>
            <span className="text-[#f1f5f9] font-medium">
              {(petType.roi_cap_multiplier * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-px bg-[#1e293b]" />
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Max Profit</span>
            <span className="text-[#00f5d4] font-medium">+{netProfit.toFixed(2)} XPET</span>
          </div>
          <div className="h-px bg-[#1e293b]" />
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Your Balance</span>
            <span className="text-[#f1f5f9] font-medium">{balance.toFixed(2)} XPET</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">After Purchase</span>
            <span className={`font-medium ${canAfford ? 'text-[#c7f464]' : 'text-red-400'}`}>
              {newBalance.toFixed(2)} XPET
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button variant="ghost" fullWidth onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            variant={canAfford ? 'lime' : 'disabled'}
            fullWidth
            onClick={onConfirm}
            disabled={!canAfford || isLoading}
            haptic="heavy"
          >
            {isLoading ? 'Processing...' : 'Recruit'}
          </Button>
        </div>
      </div>
    </div>
  );
}
