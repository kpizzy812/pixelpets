'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { Icon, type IconName } from '@/components/ui/icon';
import { useHaptic } from '@/hooks/use-haptic';

type NavItem = 'home' | 'shop' | 'tasks' | 'referrals';

interface NavItemConfig {
  id: NavItem;
  icon: IconName;
  labelKey: 'home' | 'shop' | 'tasks' | 'refs';
  href: string;
}

const NAV_ITEMS: NavItemConfig[] = [
  { id: 'home', icon: 'home', labelKey: 'home', href: '/' },
  { id: 'shop', icon: 'shop', labelKey: 'shop', href: '/shop' },
  { id: 'tasks', icon: 'tasks', labelKey: 'tasks', href: '/tasks' },
  { id: 'referrals', icon: 'referrals', labelKey: 'refs', href: '/referrals' },
];

export function BottomNav() {
  const pathname = usePathname();
  const { tap, selection } = useHaptic();
  const t = useTranslations('nav');

  const getActiveItem = (): NavItem => {
    if (pathname === '/shop') return 'shop';
    if (pathname === '/tasks') return 'tasks';
    if (pathname === '/referrals') return 'referrals';
    return 'home';
  };

  const currentItem = getActiveItem();

  const handleNavClick = useCallback(
    (itemId: NavItem) => {
      if (currentItem !== itemId) {
        selection();
      } else {
        tap();
      }
    },
    [currentItem, selection, tap]
  );

  return (
    <div className="mx-4 mb-4 p-2 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-xl">
      <div className="flex justify-around items-center">
        {NAV_ITEMS.map((item) => {
          const isActive = currentItem === item.id;
          return (
            <Link
              key={item.id}
              href={item.href}
              onClick={() => handleNavClick(item.id)}
              className={`flex flex-col items-center justify-center w-14 h-14 rounded-2xl transition-all duration-200 ${
                isActive
                  ? 'bg-[#00f5d4] shadow-[0_0_16px_rgba(0,245,212,0.4)]'
                  : 'bg-transparent hover:bg-[#1e293b]/60'
              }`}
            >
              <Icon
                name={item.icon}
                size={20}
                className={isActive ? 'text-[#050712]' : 'text-[#64748b]'}
              />
              <span
                className={`text-[9px] font-medium uppercase tracking-wide ${
                  isActive ? 'text-[#050712]' : 'text-[#64748b]'
                }`}
              >
                {t(item.labelKey)}
              </span>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
