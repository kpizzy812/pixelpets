'use client';

import { useEffect, useCallback, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { getHaptic } from './use-haptic';

interface UseBackButtonOptions {
  // Custom back handler - return true to prevent default navigation
  onBack?: () => boolean | void;
  // Whether to show the back button (auto-detected based on pathname if not provided)
  show?: boolean;
  // Fallback path when there's no history
  fallbackPath?: string;
}

function getWebApp() {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
}

// Pages that should NOT show back button (main navigation pages)
const MAIN_PAGES = ['/', '/shop', '/tasks', '/referrals'];

export function useBackButton(options: UseBackButtonOptions = {}) {
  const router = useRouter();
  const pathname = usePathname();
  const { onBack, show, fallbackPath = '/' } = options;
  const callbackRef = useRef<(() => void) | null>(null);

  // Determine if we should show based on pathname
  const shouldShow = show !== undefined ? show : !MAIN_PAGES.includes(pathname);

  const handleBack = useCallback(() => {
    const haptic = getHaptic();
    haptic.tap();

    // If custom handler provided and returns true, prevent default
    if (onBack && onBack() === true) {
      return;
    }

    // Try to go back in history, fallback to home
    if (window.history.length > 1) {
      router.back();
    } else {
      router.push(fallbackPath);
    }
  }, [onBack, router, fallbackPath]);

  useEffect(() => {
    const webApp = getWebApp();
    if (!webApp?.BackButton) return;

    // Store the callback for cleanup
    callbackRef.current = handleBack;

    if (shouldShow) {
      webApp.BackButton.show();
      webApp.BackButton.onClick(handleBack);
    } else {
      webApp.BackButton.hide();
    }

    return () => {
      if (webApp?.BackButton) {
        webApp.BackButton.offClick(handleBack);
      }
    };
  }, [shouldShow, handleBack]);

  // Hide on unmount
  useEffect(() => {
    return () => {
      const webApp = getWebApp();
      if (webApp?.BackButton && !MAIN_PAGES.includes(pathname)) {
        webApp.BackButton.hide();
      }
    };
  }, [pathname]);

  return {
    show: useCallback(() => {
      const webApp = getWebApp();
      webApp?.BackButton?.show();
    }, []),
    hide: useCallback(() => {
      const webApp = getWebApp();
      webApp?.BackButton?.hide();
    }, []),
  };
}
