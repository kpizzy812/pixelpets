'use client';

import { useRouter } from 'next/navigation';
import { Icon } from '@/components/ui/icon';
import { formatNumber } from '@/lib/format';
import { useGameStore } from '@/store/game-store';

interface HeaderBalanceProps {
  balance: number;
}

export function HeaderBalance({ balance }: HeaderBalanceProps) {
  const router = useRouter();
  const openWallet = useGameStore((state) => state.openWallet);

  return (
    <>
      <div className="mx-4 mt-2 p-4 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          {/* Balance Section */}
          <div className="flex flex-col">
            <span className="text-[10px] uppercase tracking-widest text-[#64748b] mb-1">
              Available
            </span>
            <span className="text-2xl font-bold text-[#f1f5f9]">
              ${formatNumber(balance)}
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push('/hall-of-fame')}
              className="w-11 h-11 rounded-full bg-[#fbbf24]/20 border border-[#fbbf24]/30 flex items-center justify-center hover:bg-[#fbbf24]/30 transition-colors"
            >
              <Icon name="trophy" size={20} className="text-[#fbbf24]" />
            </button>
            <button
              onClick={openWallet}
              className="w-11 h-11 rounded-full bg-[#1e293b]/60 border border-[#334155]/50 flex items-center justify-center hover:bg-[#334155]/60 transition-colors"
            >
              <Icon name="wallet" size={20} className="text-[#94a3b8]" />
            </button>
            <button
              onClick={() => router.push('/settings')}
              className="w-11 h-11 rounded-full bg-[#1e293b]/60 border border-[#334155]/50 flex items-center justify-center hover:bg-[#334155]/60 transition-colors"
            >
              <Icon name="settings" size={20} className="text-[#94a3b8]" />
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
