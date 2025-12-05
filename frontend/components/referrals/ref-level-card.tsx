'use client';

import { Icon } from '@/components/ui/icon';
import { formatNumber } from '@/lib/format';

interface RefLevelCardProps {
  level: number;
  percentage: number;
  count: number;
  earned: number;
  unlocked: boolean;
  unlockRequirement?: number;
  progress?: string;
}

export function RefLevelCard({
  level,
  percentage,
  count,
  earned,
  unlocked,
  unlockRequirement,
  progress,
}: RefLevelCardProps) {
  return (
    <div
      className={`p-3 rounded-xl border transition-all ${
        unlocked
          ? 'bg-[#0d1220]/90 border-[#1e293b]/50'
          : 'bg-[#0d1220]/50 border-[#1e293b]/30 opacity-60'
      }`}
    >
      <div className="flex items-center justify-between">
        {/* Level Info */}
        <div className="flex items-center gap-2.5">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              unlocked
                ? 'bg-[#00f5d4]/20 text-[#00f5d4]'
                : 'bg-[#1e293b]/60 text-[#64748b]'
            }`}
          >
            {unlocked ? level : <Icon name="lock" size={14} />}
          </div>
          <div>
            <div className="text-sm font-medium text-[#f1f5f9]">
              Level {level}
              {unlocked && count > 0 && (
                <span className="text-xs text-[#64748b] ml-1.5">
                  ({count} refs)
                </span>
              )}
            </div>
            {!unlocked && (
              <div className="text-[11px] text-[#64748b]">
                {progress || `Need ${unlockRequirement} active refs`}
              </div>
            )}
          </div>
        </div>

        {/* Stats */}
        <div className="text-right">
          <div className={`text-base font-bold ${unlocked ? 'text-[#c7f464]' : 'text-[#64748b]'}`}>
            {percentage}%
          </div>
          {unlocked && earned > 0 && (
            <div className="text-[11px] text-[#94a3b8]">
              +${formatNumber(earned)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
