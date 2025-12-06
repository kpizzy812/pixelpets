'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useGameStore } from '@/store/game-store';

export default function SpinPage() {
  const router = useRouter();
  const setActiveTab = useGameStore((state) => state.setActiveTab);

  useEffect(() => {
    setActiveTab('spin');
    router.replace('/');
  }, [setActiveTab, router]);

  return null;
}
