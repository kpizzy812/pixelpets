'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { WalletModal } from '@/components/wallet';
import { formatNumber } from '@/lib/format';

interface HeaderBalanceProps {
  balance: number;
}

export function HeaderBalance({ balance }: HeaderBalanceProps) {
  const router = useRouter();
  const [isWalletOpen, setIsWalletOpen] = useState(false);

  return (
    <>
      <div className="mx-4 mt-4 p-4 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
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
              className="w-11 h-11 rounded-full bg-[#fbbf24]/20 border border-[#fbbf24]/30 flex items-center justify-center text-lg hover:bg-[#fbbf24]/30 transition-colors"
            >
              <span role="img" aria-label="hall of fame">*</span>
            </button>
            <button
              onClick={() => setIsWalletOpen(true)}
              className="w-11 h-11 rounded-full bg-[#1e293b]/60 border border-[#334155]/50 flex items-center justify-center text-lg hover:bg-[#334155]/60 transition-colors"
            >
              <span role="img" aria-label="wallet">$</span>
            </button>
            <button
              onClick={() => router.push('/settings')}
              className="w-11 h-11 rounded-full bg-[#1e293b]/60 border border-[#334155]/50 flex items-center justify-center text-lg hover:bg-[#334155]/60 transition-colors"
            >
              <span role="img" aria-label="settings">@</span>
            </button>
          </div>
        </div>
      </div>

      {/* Wallet Modal */}
      <WalletModal isOpen={isWalletOpen} onClose={() => setIsWalletOpen(false)} />
    </>
  );
}
