'use client';

import { Button } from '@/components/ui/button';
import { PetImage } from '@/components/ui/pet-image';
import { Icon } from '@/components/ui/icon';
import type { PetType } from '@/types/api';

interface PetTypeCardProps {
  petType: PetType;
  onBuy: () => void;
  disabled?: boolean;
}

export function PetTypeCard({ petType, onBuy, disabled }: PetTypeCardProps) {
  return (
    <div className="p-3 rounded-2xl bg-[#0d1220]/90 border border-[#1e293b]/50 flex flex-col">
      {/* Pet Image */}
      <div className="aspect-square rounded-xl bg-[#1e293b]/40 flex items-center justify-center mb-3">
        <PetImage imageKey={petType.image_key} alt={petType.name} size={72} />
      </div>

      {/* Pet Name */}
      <h3 className="text-sm font-semibold text-[#f1f5f9] mb-1 truncate">{petType.name}</h3>

      {/* Stats */}
      <div className="flex items-center justify-between text-xs text-[#94a3b8] mb-3">
        <span className="text-[#c7f464]">+{petType.daily_rate}%</span>
        <span>{petType.roi_cap_multiplier * 100}% ROI</span>
      </div>

      {/* Price & Buy */}
      <Button
        variant={disabled ? 'disabled' : 'lime'}
        onClick={onBuy}
        disabled={disabled}
        className="w-full text-xs py-2 flex items-center justify-center gap-1"
      >
        <Icon name="coins" size={14} />
        <span>{petType.base_price}</span>
      </Button>
    </div>
  );
}
