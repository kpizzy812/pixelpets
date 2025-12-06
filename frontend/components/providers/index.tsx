'use client';

import { useEffect, useState, useCallback, type ReactNode } from 'react';
import { TelegramProvider } from './telegram-provider';
import { AuthProvider, useAuth } from '@/hooks/use-auth';
import { ToastProvider } from '@/components/ui/toast-provider';
import { AppLoader } from '@/components/ui/app-loader';
import { ErrorBoundary } from '@/components/ui/error-boundary';
import { WalletModal } from '@/components/wallet';
import { useGameStore } from '@/store/game-store';

// Suppress known Android Telegram toFixed errors globally
if (typeof window !== 'undefined') {
  const originalError = console.error;
  console.error = (...args) => {
    const msg = args[0]?.toString?.() || '';
    // Skip known Android Telegram theme_changed toFixed errors
    if (msg.includes('toFixed') && msg.includes('not a function')) {
      console.warn('[Suppressed] Android Telegram theme error:', msg);
      return;
    }
    originalError.apply(console, args);
  };

  // Global error handler for uncaught errors
  window.addEventListener('error', (event) => {
    if (event.message?.includes('toFixed')) {
      console.warn('[Global] Suppressed toFixed error');
      event.preventDefault();
      return false;
    }
  });

  window.addEventListener('unhandledrejection', (event) => {
    if (event.reason?.message?.includes('toFixed')) {
      console.warn('[Global] Suppressed toFixed rejection');
      event.preventDefault();
    }
  });
}

interface ProvidersProps {
  children: ReactNode;
}

// Inner component that uses auth context
function AppContent({ children }: { children: ReactNode }) {
  const { isLoading: authLoading, isAuthenticated, user } = useAuth();
  const { fetchPets, fetchPetCatalog, fetchTasks, fetchReferrals, setUser } = useGameStore();
  const isWalletOpen = useGameStore((state) => state.isWalletOpen);
  const closeWallet = useGameStore((state) => state.closeWallet);
  const [isAppReady, setIsAppReady] = useState(false);
  const [showLoader, setShowLoader] = useState(true);

  // Preload all data when authenticated
  useEffect(() => {
    const preloadData = async () => {
      if (isAuthenticated && user) {
        // Always sync fresh user data to game store
        setUser(user);
        // Load ALL essential data in parallel for instant tab switching
        await Promise.all([
          fetchPets(),
          fetchPetCatalog(),
          fetchTasks(),
          fetchReferrals(),
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
  }, [authLoading, isAuthenticated, user, fetchPets, fetchPetCatalog, fetchTasks, fetchReferrals, setUser]);

  // Keep game store user in sync when auth user changes (e.g., balance updated)
  useEffect(() => {
    if (user) {
      setUser(user);
    }
  }, [user, setUser]);

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

  return (
    <>
      {children}
      <WalletModal isOpen={isWalletOpen} onClose={closeWallet} />
    </>
  );
}

export function Providers({ children }: ProvidersProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // TelegramProvider handles mock mode internally
    setIsMounted(true);
  }, []);

  // Prevent hydration mismatch
  if (!isMounted) {
    return null;
  }

  return (
    <ErrorBoundary>
      <TelegramProvider>
        <AuthProvider>
          <AppContent>{children}</AppContent>
          <ToastProvider />
        </AuthProvider>
      </TelegramProvider>
    </ErrorBoundary>
  );
}
