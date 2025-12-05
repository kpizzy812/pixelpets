'use client';

import { useEffect, useState, useCallback, type ReactNode } from 'react';
import { TelegramProvider } from './telegram-provider';
import { AuthProvider, useAuth } from '@/hooks/use-auth';
import { ToastProvider } from '@/components/ui/toast-provider';
import { AppLoader } from '@/components/ui/app-loader';
import { setupTelegramMock } from '@/lib/telegram-mock';
import { useGameStore } from '@/store/game-store';

interface ProvidersProps {
  children: ReactNode;
}

// Inner component that uses auth context
function AppContent({ children }: { children: ReactNode }) {
  const { isLoading: authLoading, isAuthenticated, user } = useAuth();
  const { fetchPets, fetchPetCatalog, setUser } = useGameStore();
  const [isAppReady, setIsAppReady] = useState(false);
  const [showLoader, setShowLoader] = useState(true);

  // Preload all data when authenticated
  useEffect(() => {
    const preloadData = async () => {
      if (isAuthenticated && user) {
        setUser(user);
        // Load essential data in parallel
        await Promise.all([
          fetchPets(),
          fetchPetCatalog(),
        ]);
        setIsAppReady(true);
      }
    };

    if (!authLoading) {
      if (isAuthenticated) {
        preloadData();
      } else {
        // Not authenticated, skip preload
        setIsAppReady(true);
      }
    }
  }, [authLoading, isAuthenticated, user, fetchPets, fetchPetCatalog, setUser]);

  const handleLoaderComplete = useCallback(() => {
    setShowLoader(false);
  }, []);

  // Show loader until app is ready
  if (showLoader && (!isAppReady || authLoading)) {
    return <AppLoader onComplete={handleLoaderComplete} />;
  }

  // After loader animation completes, show app
  if (showLoader) {
    return <AppLoader onComplete={handleLoaderComplete} />;
  }

  return <>{children}</>;
}

export function Providers({ children }: ProvidersProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // Setup mock in dev mode (outside Telegram)
    if (process.env.NODE_ENV === 'development') {
      setupTelegramMock();
    }
    setIsMounted(true);
  }, []);

  // Prevent hydration mismatch
  if (!isMounted) {
    return null;
  }

  return (
    <TelegramProvider>
      <AuthProvider>
        <AppContent>{children}</AppContent>
        <ToastProvider />
      </AuthProvider>
    </TelegramProvider>
  );
}
