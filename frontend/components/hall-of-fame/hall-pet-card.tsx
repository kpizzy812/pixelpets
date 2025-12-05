'use client';

import { PetImage } from '@/components/ui/pet-image';
import { formatNumber } from '@/lib/format';
import type { HallOfFameEntry } from '@/types/api';

interface HallPetCardProps {
  pet: HallOfFameEntry;
  rank: number;
}

const RANK_BADGES: Record<number, { emoji: string; color: string }> = {
  1: { emoji: '1', color: 'text-[#fbbf24]' },
  2: { emoji: '2', color: 'text-[#94a3b8]' },
  3: { emoji: '3', color: 'text-[#cd7f32]' },
};

export function HallPetCard({ pet, rank }: HallPetCardProps) {
  const badge = RANK_BADGES[rank];
  const roi = formatNumber((pet.total_farmed / pet.invested_total) * 100, 0);
  const evolvedDate = pet.evolved_at
    ? new Date(pet.evolved_at).toLocaleDateString()
    : 'Unknown';

  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
      <div className="flex items-center gap-4">
        {/* Rank Badge */}
        <div className="w-10 h-10 rounded-full bg-[#1e293b]/60 flex items-center justify-center">
          {badge ? (
            <span className={`text-xl ${badge.color}`}>{badge.emoji}</span>
          ) : (
            <span className="text-sm font-bold text-[#64748b]">#{rank}</span>
          )}
        </div>

        {/* Pet Icon */}
        <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#fbbf24]/20 to-transparent border border-[#fbbf24]/30 flex items-center justify-center">
          <PetImage imageKey={pet.pet_type.image_key} alt={pet.pet_type.name} size={48} />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-[#f1f5f9] truncate">{pet.pet_type.name}</h3>
            <span className="px-2 py-0.5 rounded-md bg-[#fbbf24]/20 text-[#fbbf24] text-xs">
              Mythic
            </span>
          </div>
          <p className="text-xs text-[#64748b] mt-1">
            Invested: {formatNumber(pet.invested_total)} XPET
          </p>
        </div>

        {/* Earnings */}
        <div className="text-right">
          <div className="text-lg font-bold text-[#c7f464]">
            +{formatNumber(pet.total_farmed)}
          </div>
          <div className="text-xs text-[#64748b]">{roi}% ROI</div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-3 pt-3 border-t border-[#1e293b]/50 flex justify-between items-center">
        <span className="text-xs text-[#64748b]">Evolved on {evolvedDate}</span>
        <div className="flex items-center gap-1">
          <span className="text-xs text-[#fbbf24]">*</span>
          <span className="text-xs text-[#94a3b8]">Legend</span>
        </div>
      </div>
    </div>
  );
}
