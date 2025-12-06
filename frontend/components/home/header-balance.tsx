'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Icon } from '@/components/ui/icon';
import { formatNumber } from '@/lib/format';
import { useGameStore } from '@/store/game-store';
import { useTelegram } from '@/components/providers/telegram-provider';

interface HeaderBalanceProps {
  balance: number;
}

export function HeaderBalance({ balance }: HeaderBalanceProps) {
  const router = useRouter();
  const t = useTranslations('common');
  const openWallet = useGameStore((state) => state.openWallet);
  const { user } = useTelegram();
  const [menuOpen, setMenuOpen] = useState(false);

  // Get user avatar photo URL from Telegram
  const getAvatarUrl = () => {
    if (!user) return null;
    // Telegram provides photo_url for profile pictures in WebApp
    // If not available, we'll show initials
    return null; // Will be replaced with actual photo_url when available
  };

  const getUserInitials = () => {
    if (!user) return 'U';
    const firstInitial = user.first_name?.[0] || '';
    const lastInitial = user.last_name?.[0] || '';
    return (firstInitial + lastInitial).toUpperCase() || 'U';
  };

  const avatarUrl = getAvatarUrl();

  return (
    <div className="relative mx-4 mt-2">
      {/* Main Header Bar */}
      <div className="flex items-center justify-between p-3 rounded-2xl bg-gradient-to-r from-[#1e293b]/90 to-[#0d1220]/90 border border-[#334155]/40 backdrop-blur-md shadow-lg">
        {/* Avatar */}
        <div className="flex-shrink-0">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="Avatar"
              className="w-12 h-12 rounded-full border-2 border-[#00f5d4]/30"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#00f5d4] to-[#c7f464] flex items-center justify-center text-[#050712] font-bold text-lg">
              {getUserInitials()}
            </div>
          )}
        </div>

        {/* Balance Section */}
        <div className="flex-1 flex flex-col items-center px-4">
          <span className="text-[9px] uppercase tracking-[0.15em] text-[#94a3b8] font-semibold mb-0.5">
            {t('balance')}
          </span>
          <span className="text-2xl font-bold bg-gradient-to-r from-[#f1f5f9] to-[#cbd5e1] bg-clip-text text-transparent">
            ${formatNumber(balance)}
          </span>
        </div>

        {/* Burger Menu Button */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="flex-shrink-0 w-12 h-12 rounded-full bg-[#1e293b]/80 border border-[#334155]/60 flex items-center justify-center hover:bg-[#334155]/80 hover:border-[#00f5d4]/40 transition-all active:scale-95"
        >
          <Icon
            name="menu"
            size={22}
            className={`text-[#94a3b8] transition-transform ${menuOpen ? 'rotate-90' : ''}`}
          />
        </button>
      </div>

      {/* Dropdown Menu */}
      {menuOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setMenuOpen(false)}
          />

          {/* Menu Items */}
          <div className="absolute right-4 top-[68px] z-50 w-auto rounded-xl bg-[#0d1220]/95 border border-[#1e293b]/70 backdrop-blur-xl shadow-2xl overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="flex flex-col gap-2 p-3">
              <button
                onClick={() => {
                  setMenuOpen(false);
                  router.push('/hall-of-fame');
                }}
                className="flex items-center justify-center w-16 h-16 rounded-xl bg-[#fbbf24]/15 border border-[#fbbf24]/25 hover:bg-[#fbbf24]/25 transition-all active:scale-95"
              >
                <Icon name="trophy" size={40} className="text-[#fbbf24]" />
              </button>

              <button
                onClick={() => {
                  setMenuOpen(false);
                  openWallet();
                }}
                className="flex items-center justify-center w-16 h-16 rounded-xl bg-[#00f5d4]/15 border border-[#00f5d4]/25 hover:bg-[#00f5d4]/25 transition-all active:scale-95"
              >
                <Icon name="wallet" size={40} className="text-[#00f5d4]" />
              </button>

              <button
                onClick={() => {
                  setMenuOpen(false);
                  router.push('/settings');
                }}
                className="flex items-center justify-center w-16 h-16 rounded-xl bg-[#94a3b8]/15 border border-[#94a3b8]/25 hover:bg-[#94a3b8]/25 transition-all active:scale-95"
              >
                <Icon name="settings" size={40} className="text-[#94a3b8]" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
