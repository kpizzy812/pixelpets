'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useCallback } from 'react';
import { Icon, type IconName } from '@/components/ui/icon';
import { useHaptic } from '@/hooks/use-haptic';

type NavItem = 'home' | 'shop' | 'spin' | 'tasks' | 'referrals';

interface NavItemConfig {
  id: NavItem;
  icon: IconName;
  href: string;
}

const NAV_ITEMS: NavItemConfig[] = [
  { id: 'home', icon: 'home', href: '/' },
  { id: 'shop', icon: 'shop', href: '/shop' },
  { id: 'spin', icon: 'spin', href: '/spin' },
  { id: 'tasks', icon: 'tasks', href: '/tasks' },
  { id: 'referrals', icon: 'referrals', href: '/referrals' },
];

export function BottomNav() {
  const pathname = usePathname();
  const { tap, selection } = useHaptic();

  const getActiveItem = (): NavItem => {
    if (pathname === '/shop') return 'shop';
    if (pathname === '/spin') return 'spin';
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
    <div className="mx-4 mb-4 p-3 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-xl">
      <div className="flex justify-around items-center">
        {NAV_ITEMS.map((item) => {
          const isActive = currentItem === item.id;
          return (
            <Link
              key={item.id}
              href={item.href}
              onClick={() => handleNavClick(item.id)}
              className={`flex items-center justify-center w-16 h-16 rounded-xl transition-all duration-200 ${
                isActive
                  ? 'bg-[#00f5d4] shadow-[0_0_16px_rgba(0,245,212,0.4)]'
                  : 'bg-transparent hover:bg-[#1e293b]/60'
              }`}
            >
              <Icon
                name={item.icon}
                size={40}
                className={isActive ? 'text-[#050712]' : 'text-[#64748b]'}
              />
            </Link>
          );
        })}
      </div>
    </div>
  );
}
