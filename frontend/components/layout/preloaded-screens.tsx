'use client';

import { HomeScreen } from '@/components/home';
import { ShopScreen } from '@/components/shop';
import { TasksScreen } from '@/components/tasks';
import { ReferralsScreen } from '@/components/referrals';
import { SpinScreen } from '@/components/spin';
import { BottomNav } from './bottom-nav';
import { FloatingSpinButton } from './floating-spin-button';
import { useBackButton } from '@/hooks/use-back-button';
import type { TabId } from '@/store/game-store';

interface PreloadedScreensProps {
  activeTab: TabId;
}

export function PreloadedScreens({ activeTab }: PreloadedScreensProps) {
  // Handle Telegram back button for non-home tabs
  useBackButton();

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Background - transparent to show body background image */}
      <div className="fixed inset-0 pointer-events-none" />

      {/* Content */}
      <div className="relative flex flex-col h-full z-10 tg-safe-top">
        {/* Screens Container */}
        <div className="flex-1 overflow-hidden">
          {/* Home Screen */}
          <div
            className="h-full"
            style={{ display: activeTab === 'home' ? 'block' : 'none' }}
          >
            <HomeScreen />
          </div>

          {/* Shop Screen */}
          <div
            className="h-full"
            style={{ display: activeTab === 'shop' ? 'block' : 'none' }}
          >
            <ShopScreen />
          </div>

          {/* Tasks Screen */}
          <div
            className="h-full"
            style={{ display: activeTab === 'tasks' ? 'block' : 'none' }}
          >
            <TasksScreen />
          </div>

          {/* Referrals Screen */}
          <div
            className="h-full"
            style={{ display: activeTab === 'referrals' ? 'block' : 'none' }}
          >
            <ReferralsScreen />
          </div>

          {/* Spin Screen */}
          <div
            className="h-full"
            style={{ display: activeTab === 'spin' ? 'block' : 'none' }}
          >
            <SpinScreen />
          </div>
        </div>

        {/* Bottom Navigation - shared across all screens */}
        <BottomNav />

        {/* Floating Spin Button - hidden on spin screen */}
        <FloatingSpinButton />
      </div>
    </div>
  );
}
