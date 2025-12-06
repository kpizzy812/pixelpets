'use client';

import { useRouter } from 'next/navigation';
import { useHaptic } from '@/hooks/use-haptic';

export function FloatingSpinButton() {
  const router = useRouter();
  const { tap } = useHaptic();

  const handleClick = () => {
    tap();
    router.push('/spin');
  };

  return (
    <button
      onClick={handleClick}
      className="fixed right-6 bottom-24 z-[100] w-20 h-20 rounded-2xl bg-gradient-to-br from-[#c7f464] to-[#00f5d4] shadow-[0_0_24px_rgba(199,244,100,0.6)] flex items-center justify-center animate-pulse-scale active:scale-95 transition-transform"
    >
      <img
        src="/pixelicons/spin.png"
        alt="Spin"
        className="w-12 h-12 object-contain"
      />
    </button>
  );
}
