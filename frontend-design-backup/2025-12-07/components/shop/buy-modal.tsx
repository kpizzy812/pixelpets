'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useHaptic } from '@/hooks/use-haptic';
import { formatNumber } from '@/lib/format';
import type { PetType } from '@/types/api';

interface BuyModalProps {
  petType: PetType;
  balance: number;
  onConfirm: () => void;
  onClose: () => void;
  isLoading?: boolean;
}

export function BuyModal({ petType, balance, onConfirm, onClose, isLoading }: BuyModalProps) {
  const router = useRouter();
  const { impact, tap } = useHaptic();
  const maxProfit = petType.base_price * petType.roi_cap_multiplier;
  const netProfit = maxProfit - petType.base_price;
  const newBalance = balance - petType.base_price;
  const canAfford = balance >= petType.base_price;

  const handleInsufficientBalance = () => {
    tap();
    onClose();
    router.push('/wallet');
  };

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
            <PetImage imageKey={petType.image_key} level="BABY" alt={petType.name} size={80} />
          </div>
          <h2 className="text-xl font-bold text-[#f1f5f9]">{petType.name}</h2>
          <p className="text-sm text-[#64748b] mt-1">Confirm recruitment</p>
        </div>

        {/* Stats */}
        <div className="space-y-3 mb-6">
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Price</span>
            <span className="text-[#f1f5f9] font-medium inline-flex items-center gap-1">{petType.base_price} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Daily Rate</span>
            <span className="text-[#c7f464] font-medium">+{petType.daily_rate}%</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">ROI Cap</span>
            <span className="text-[#f1f5f9] font-medium">
              {formatNumber(petType.roi_cap_multiplier * 100, 0)}%
            </span>
          </div>
          <div className="h-px bg-[#1e293b]" />
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Max Profit</span>
            <span className="text-[#00f5d4] font-medium inline-flex items-center gap-1">+{formatNumber(netProfit)} <XpetCoin size={18} /></span>
          </div>
          <div className="h-px bg-[#1e293b]" />
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">Your Balance</span>
            <span className="text-[#f1f5f9] font-medium inline-flex items-center gap-1">{formatNumber(balance)} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#94a3b8]">After Purchase</span>
            <span className={`font-medium ${canAfford ? 'text-[#c7f464]' : 'text-red-400'}`}>
              {formatNumber(newBalance)} <XpetCoin size={18} />
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <Button variant="ghost" fullWidth onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          {canAfford ? (
            <Button
              variant="lime"
              fullWidth
              onClick={onConfirm}
              disabled={isLoading}
              haptic="heavy"
            >
              {isLoading ? 'Processing...' : 'Recruit'}
            </Button>
          ) : (
            <Button
              variant="lime"
              fullWidth
              onClick={handleInsufficientBalance}
              haptic="medium"
            >
              Top Up Balance
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
