'use client';

import { Icon } from '@/components/ui/icon';
import { formatNumber } from '@/lib/format';

interface RefLevelCardProps {
  level: number;
  percentage: number;
  count: number;
  earned: number;
  unlocked: boolean;
}

export function RefLevelCard({
  level,
  percentage,
  count,
  earned,
  unlocked,
}: RefLevelCardProps) {
  const getRequiredRefs = (lvl: number): number => {
    switch (lvl) {
      case 1: return 0;
      case 2: return 3;
      case 3: return 5;
      case 4: return 10;
      case 5: return 20;
      default: return 0;
    }
  };

  const requiredRefs = getRequiredRefs(level);

  return (
    <div
      className={`p-4 rounded-2xl border transition-all ${
        unlocked
          ? 'bg-[#0d1220]/90 border-[#1e293b]/50'
          : 'bg-[#0d1220]/50 border-[#1e293b]/30 opacity-60'
      }`}
    >
      <div className="flex items-center justify-between">
        {/* Level Info */}
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
              unlocked
                ? 'bg-[#00f5d4]/20 text-[#00f5d4]'
                : 'bg-[#1e293b]/60 text-[#64748b]'
            }`}
          >
            {unlocked ? level : <Icon name="lock" size={18} />}
          </div>
          <div>
            <div className="text-sm font-medium text-[#f1f5f9]">
              Level {level}
            </div>
            <div className="text-xs text-[#64748b]">
              {unlocked
                ? `${count} referrals`
                : `Unlock at ${requiredRefs} active refs`}
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="text-right">
          <div className={`text-lg font-bold ${unlocked ? 'text-[#c7f464]' : 'text-[#64748b]'}`}>
            {percentage}%
          </div>
          {unlocked && earned > 0 && (
            <div className="text-xs text-[#94a3b8]">
              +${formatNumber(earned)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
