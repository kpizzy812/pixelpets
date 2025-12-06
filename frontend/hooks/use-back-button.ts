'use client';

import { useEffect, useCallback, useRef } from 'react';
import { getHaptic } from './use-haptic';
import { useGameStore, useActiveTab, type TabId } from '@/store/game-store';

interface UseBackButtonOptions {
  // Custom back handler - return true to prevent default navigation
  onBack?: () => boolean | void;
  // Whether to show the back button (auto-detected based on activeTab if not provided)
  show?: boolean;
}

function getWebApp() {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
}

// Tabs that should NOT show back button (main navigation tabs)
const MAIN_TABS: TabId[] = ['home', 'shop', 'tasks', 'referrals'];

export function useBackButton(options: UseBackButtonOptions = {}) {
  const activeTab = useActiveTab();
  const setActiveTab = useGameStore((state) => state.setActiveTab);
  const { onBack, show } = options;
  const callbackRef = useRef<(() => void) | null>(null);

  // Determine if we should show based on activeTab
  // Show back button only for secondary screens (like spin)
  const shouldShow = show !== undefined ? show : !MAIN_TABS.includes(activeTab);

  const handleBack = useCallback(() => {
    const haptic = getHaptic();
    haptic.tap();

    // If custom handler provided and returns true, prevent default
    if (onBack && onBack() === true) {
      return;
    }

    // Go back to home tab
    setActiveTab('home');
  }, [onBack, setActiveTab]);

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
      if (webApp?.BackButton && !MAIN_TABS.includes(activeTab)) {
        webApp.BackButton.hide();
      }
    };
  }, [activeTab]);

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
