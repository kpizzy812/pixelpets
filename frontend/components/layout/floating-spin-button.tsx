'use client';

import { useHaptic } from '@/hooks/use-haptic';
import { useGameStore, useActiveTab } from '@/store/game-store';

export function FloatingSpinButton() {
  const activeTab = useActiveTab();
  const setActiveTab = useGameStore((state) => state.setActiveTab);
  const { tap } = useHaptic();

  // Don't show on spin screen
  if (activeTab === 'spin') {
    return null;
  }

  const handleClick = () => {
    tap();
    setActiveTab('spin');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed right-6 bottom-24 z-[100] flex items-center justify-center animate-pulse-scale active:scale-95 transition-transform"
    >
      <img
        src="/pixelicons/spin.png"
        alt="Spin"
        className="w-20 h-20 object-contain drop-shadow-[0_0_12px_rgba(199,244,100,0.6)]"
      />
    </button>
  );
}
