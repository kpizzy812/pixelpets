'use client';

import { useCallback } from 'react';
import { Icon, type IconName } from '@/components/ui/icon';
import { useHaptic } from '@/hooks/use-haptic';
import { useGameStore, useActiveTab, type TabId } from '@/store/game-store';

interface NavItemConfig {
  id: TabId;
  icon: IconName;
}

const NAV_ITEMS: NavItemConfig[] = [
  { id: 'home', icon: 'home' },
  { id: 'shop', icon: 'shop' },
  { id: 'tasks', icon: 'tasks' },
  { id: 'referrals', icon: 'referrals' },
];

export function BottomNav() {
  const activeTab = useActiveTab();
  const setActiveTab = useGameStore((state) => state.setActiveTab);
  const { tap, selection } = useHaptic();

  const handleNavClick = useCallback(
    (itemId: TabId) => {
      if (activeTab !== itemId) {
        selection();
        setActiveTab(itemId);
      } else {
        tap();
      }
    },
    [activeTab, selection, tap, setActiveTab]
  );

  return (
    <div className="mx-4 mb-4 p-3 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-xl">
      <div className="flex justify-around items-center">
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
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
            </button>
          );
        })}
      </div>
    </div>
  );
}
