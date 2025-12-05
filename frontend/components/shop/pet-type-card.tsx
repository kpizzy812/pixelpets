'use client';

import { Button } from '@/components/ui/button';
import { XpetCoin } from '@/components/ui/xpet-coin';
import type { PetType } from '@/types/api';

interface PetTypeCardProps {
  petType: PetType;
  onBuy: () => void;
  disabled?: boolean;
}

export function PetTypeCard({ petType, onBuy, disabled }: PetTypeCardProps) {
  // daily_rate comes as decimal (0.01 = 1%), convert to percentage
  // Round to avoid floating point issues (e.g., 0.022 * 100 = 2.1999999...)
  const dailyPercent = Math.round(petType.daily_rate * 1000) / 10;

  return (
    <div className="rounded-2xl bg-[#0d1220]/90 border border-[#1e293b]/50 flex flex-col overflow-hidden">
      {/* Pet Image - Full width, clipped with rounded corners */}
      <div className="aspect-square overflow-hidden rounded-t-2xl">
        <img
          src={`/pets/${petType.image_key}.png`}
          alt={petType.name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Content */}
      <div className="p-3">
        {/* Pet Name */}
        <h3 className="text-sm font-semibold text-[#f1f5f9] mb-1 truncate">{petType.name}</h3>

        {/* Stats */}
        <div className="flex items-center justify-between text-xs text-[#94a3b8] mb-3">
          <span className="text-[#c7f464]">+{dailyPercent}%</span>
          <span>{petType.roi_cap_multiplier * 100}% ROI</span>
        </div>

        {/* Price & Buy */}
        <Button
          variant={disabled ? 'disabled' : 'lime'}
          onClick={onBuy}
          disabled={disabled}
          className="w-full text-xs py-2 flex items-center justify-center gap-1"
        >
          <XpetCoin size={14} />
          <span>{petType.base_price}</span>
        </Button>
      </div>
    </div>
  );
}
