'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { Icon } from '@/components/ui/icon';
import { formatNumber } from '@/lib/format';
import { useGameStore } from '@/store/game-store';
import { useTelegram } from '@/components/providers/telegram-provider';
import { useHaptic } from '@/hooks/use-haptic';

interface HeaderBalanceProps {
  balance: number;
}

export function HeaderBalance({ balance }: HeaderBalanceProps) {
  const router = useRouter();
  const t = useTranslations('common');
  const openWallet = useGameStore((state) => state.openWallet);
  const { user } = useTelegram();
  const { tap } = useHaptic();
  const [menuOpen, setMenuOpen] = useState(false);

  // Get user avatar photo URL from Telegram
  const getAvatarUrl = () => {
    if (!user) return null;
    // Telegram provides photo_url for profile pictures in WebApp
    return user.photo_url || null;
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
      <div className="flex items-center justify-between py-2">
        {/* Avatar - clickable to open profile */}
        <button
          onClick={() => {
            tap();
            router.push('/profile');
          }}
          className="flex-shrink-0 active:scale-95 transition-transform"
        >
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt="Avatar"
              className="w-12 h-12 rounded-full border-2 border-[#00f5d4]/30 hover:border-[#00f5d4]/60 transition-colors"
            />
          ) : (
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#00f5d4] to-[#c7f464] flex items-center justify-center text-[#050712] font-bold text-lg hover:opacity-90 transition-opacity">
              {getUserInitials()}
            </div>
          )}
        </button>

        {/* Balance Section with rounded background */}
        <div className="flex flex-col items-center px-5 py-2 rounded-full bg-[#0d1220]/80 border border-[#1e293b]/60 backdrop-blur-sm">
          <span className="text-[9px] uppercase tracking-[0.15em] text-[#94a3b8] font-semibold mb-0.5">
            {t('balance')}
          </span>
          <div className="flex items-center gap-2">
            <Image src="/XPET.png" alt="XPET" width={24} height={24} />
            <span className="text-xl font-bold bg-gradient-to-r from-[#c7f464] to-[#a3d944] bg-clip-text text-transparent">
              {formatNumber(balance)}
            </span>
            <span className="text-xs text-[#64748b]">
              (${formatNumber(balance)})
            </span>
          </div>
        </div>

        {/* Burger Menu Button */}
        <button
          onClick={() => { tap(); setMenuOpen(!menuOpen); }}
          className="flex-shrink-0 w-12 h-12 rounded-full bg-[#1e293b]/80 border border-[#334155]/60 flex items-center justify-center hover:bg-[#334155]/80 hover:border-[#00f5d4]/40 transition-all active:scale-95"
        >
          <Icon
            name={menuOpen ? 'close' : 'menu'}
            size={22}
            className="text-[#94a3b8]"
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
                  tap();
                  setMenuOpen(false);
                  router.push('/hall-of-fame');
                }}
                className="flex items-center justify-center w-16 h-16 rounded-xl bg-[#fbbf24]/15 border border-[#fbbf24]/25 hover:bg-[#fbbf24]/25 transition-all active:scale-95"
              >
                <Icon name="trophy" size={40} className="text-[#fbbf24]" />
              </button>

              <button
                onClick={() => {
                  tap();
                  setMenuOpen(false);
                  openWallet();
                }}
                className="flex items-center justify-center w-16 h-16 rounded-xl bg-[#00f5d4]/15 border border-[#00f5d4]/25 hover:bg-[#00f5d4]/25 transition-all active:scale-95"
              >
                <Icon name="wallet" size={40} className="text-[#00f5d4]" />
              </button>

              <button
                onClick={() => {
                  tap();
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
