'use client';

import { formatNumber } from '@/lib/format';

interface RefStatsCardProps {
  totalReferrals: number;
  activeReferrals: number;
  totalEarned: number;
}

export function RefStatsCard({
  totalReferrals,
  activeReferrals,
  totalEarned,
}: RefStatsCardProps) {
  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/90 border border-[#1e293b]/50">
      <div className="grid grid-cols-3 gap-4 text-center">
        <div>
          <div className="text-2xl font-bold text-[#f1f5f9]">{totalReferrals}</div>
          <div className="text-xs text-[#64748b] mt-1">Total</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-[#00f5d4]">{activeReferrals}</div>
          <div className="text-xs text-[#64748b] mt-1">Active</div>
        </div>
        <div>
          <div className="text-2xl font-bold text-[#c7f464]">
            ${formatNumber(totalEarned)}
          </div>
          <div className="text-xs text-[#64748b] mt-1">Earned</div>
        </div>
      </div>
    </div>
  );
}
