'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useGameStore } from '@/store/game-store';

export default function TasksPage() {
  const router = useRouter();
  const setActiveTab = useGameStore((state) => state.setActiveTab);

  useEffect(() => {
    setActiveTab('tasks');
    router.replace('/');
  }, [setActiveTab, router]);

  return null;
}
