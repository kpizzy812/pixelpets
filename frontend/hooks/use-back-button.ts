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

// Track SDK back button state
let backButtonModule: {
  show: () => void;
  hide: () => void;
  onClick: (handler: () => void) => () => void;
  isSupported: () => boolean;
} | null = null;

let isModuleLoading = false;
let moduleLoadPromise: Promise<void> | null = null;

async function loadBackButtonModule() {
  if (backButtonModule) return backButtonModule;
  if (isModuleLoading && moduleLoadPromise) {
    await moduleLoadPromise;
    return backButtonModule;
  }

  isModuleLoading = true;
  moduleLoadPromise = (async () => {
    try {
      const sdk = await import('@telegram-apps/sdk-react');
      const { backButton } = sdk;

      // Mount back button if available
      if (backButton.mount.isAvailable()) {
        backButton.mount();
      }

      backButtonModule = {
        show: () => {
          if (backButton.show.isAvailable()) {
            backButton.show();
          }
        },
        hide: () => {
          if (backButton.hide.isAvailable()) {
            backButton.hide();
          }
        },
        onClick: (handler: () => void) => {
          if (backButton.onClick.isAvailable()) {
            return backButton.onClick(handler);
          }
          return () => {};
        },
        isSupported: () => backButton.isSupported(),
      };
    } catch (error) {
      console.warn('[BackButton] Failed to load SDK:', error);
      backButtonModule = null;
    }
  })();

  await moduleLoadPromise;
  isModuleLoading = false;
  return backButtonModule;
}

// Pages that should NOT show back button (main navigation pages)
const MAIN_PAGES = ['/', '/shop', '/tasks', '/referrals'];

export function useBackButton(options: UseBackButtonOptions = {}) {
  const router = useRouter();
  const pathname = usePathname();
  const { onBack, show, fallbackPath = '/' } = options;
  const cleanupRef = useRef<(() => void) | null>(null);

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
    let isMounted = true;

    const setup = async () => {
      const module = await loadBackButtonModule();
      if (!module || !isMounted) return;

      // Clean up previous handler
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }

      if (shouldShow) {
        module.show();
        cleanupRef.current = module.onClick(handleBack);
      } else {
        module.hide();
      }
    };

    setup();

    return () => {
      isMounted = false;
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }
    };
  }, [shouldShow, handleBack]);

  // Hide on unmount
  useEffect(() => {
    return () => {
      loadBackButtonModule().then((module) => {
        if (module && !MAIN_PAGES.includes(pathname)) {
          module.hide();
        }
      });
    };
  }, [pathname]);

  return {
    show: useCallback(async () => {
      const module = await loadBackButtonModule();
      module?.show();
    }, []),
    hide: useCallback(async () => {
      const module = await loadBackButtonModule();
      module?.hide();
    }, []),
  };
}
