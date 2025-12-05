'use client';

import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { formatNumber } from '@/lib/format';
import type { PetType } from '@/types/api';

interface PetTypeCardProps {
  petType: PetType;
  onBuy: () => void;
  disabled?: boolean;
}

export function PetTypeCard({ petType, onBuy, disabled }: PetTypeCardProps) {
  const getRarityFromPrice = (price: number): string => {
    if (price >= 300) return 'Legendary';
    if (price >= 150) return 'Epic';
    if (price >= 100) return 'Rare';
    if (price >= 50) return 'Uncommon';
    return 'Common';
  };

  const getRarityColor = (rarity: string): string => {
    switch (rarity) {
      case 'Legendary': return 'text-[#fbbf24] border-[#fbbf24]/30';
      case 'Epic': return 'text-[#a855f7] border-[#a855f7]/30';
      case 'Rare': return 'text-[#00f5d4] border-[#00f5d4]/30';
      case 'Uncommon': return 'text-[#c7f464] border-[#c7f464]/30';
      default: return 'text-[#94a3b8] border-[#94a3b8]/30';
    }
  };

  const getRarityGradient = (rarity: string): string => {
    switch (rarity) {
      case 'Legendary': return 'from-[#fbbf24]/10 via-transparent to-transparent';
      case 'Epic': return 'from-[#a855f7]/10 via-transparent to-transparent';
      case 'Rare': return 'from-[#00f5d4]/10 via-transparent to-transparent';
      case 'Uncommon': return 'from-[#c7f464]/10 via-transparent to-transparent';
      default: return 'from-[#94a3b8]/10 via-transparent to-transparent';
    }
  };

  const rarity = getRarityFromPrice(petType.base_price);
  const rarityColor = getRarityColor(rarity);
  const rarityGradient = getRarityGradient(rarity);

  return (
    <div className={`p-4 rounded-2xl bg-gradient-to-r ${rarityGradient} bg-[#0d1220]/90 border border-[#1e293b]/50`}>
      <div className="flex items-center gap-4">
        {/* Pet Image */}
        <div className="w-16 h-16 rounded-xl bg-[#1e293b]/60 flex items-center justify-center">
          <PetImage imageKey={petType.image_key} alt={petType.name} size={56} />
        </div>

        {/* Pet Info */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-lg font-semibold text-[#f1f5f9]">{petType.name}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full border ${rarityColor}`}>
              {rarity}
            </span>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <span className="text-[#c7f464]">+{petType.daily_rate}%/day</span>
            <span className="text-[#64748b]">
              {formatNumber(petType.roi_cap_multiplier * 100, 0)}% ROI
            </span>
          </div>
        </div>

        {/* Price & Buy */}
        <div className="text-right">
          <div className="text-lg font-bold text-[#f1f5f9] mb-2">
            {petType.base_price} XPET
          </div>
          <Button
            variant={disabled ? 'disabled' : 'lime'}
            onClick={onBuy}
            disabled={disabled}
            className="text-xs px-4 py-2"
          >
            Recruit
          </Button>
        </div>
      </div>
    </div>
  );
}
