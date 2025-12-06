'use client';

import { PreloadedScreens } from '@/components/layout/preloaded-screens';
import { useActiveTab } from '@/store/game-store';

export default function HomePage() {
  const activeTab = useActiveTab();

  return (
    <main className="app-container">
      <PreloadedScreens activeTab={activeTab} />
    </main>
  );
}
