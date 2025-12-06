'use client';

import { useEffect, useRef, useState, createContext, useContext, type ReactNode } from 'react';
import { isTelegramMiniApp } from '@/lib/environment';
import type { WebApp } from '@/types/telegram';

/**
 * TelegramProvider - Proper Telegram Mini App initialization
 *
 * Best Practices 2025:
 * 1. Correct sequence: ready() → expand() → requestFullscreen()
 * 2. Safe Areas support for iOS notch
 * 3. Theme Parameters integration
 * 4. Header and background colors setup
 * 5. Disable vertical swipes
 * 6. Closing confirmation
 */

// Mock user for development (only used outside Telegram)
const MOCK_USER = {
  id: 123456789,
  first_name: 'Dev',
  last_name: 'User',
  username: 'devuser',
  language_code: 'en',
  is_premium: false,
  allows_write_to_pm: true,
};

interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  allows_write_to_pm?: boolean;
}

interface TelegramContextValue {
  isReady: boolean;
  isTelegram: boolean;
  user: TelegramUser | null;
  rawInitData: string | null;
  startParam: string | null; // Referral code from startapp URL param
  colorScheme: 'light' | 'dark';
  isFullscreen: boolean;
  webApp: WebApp | null;
}

const TelegramContext = createContext<TelegramContextValue>({
  isReady: false,
  isTelegram: false,
  user: null,
  rawInitData: null,
  startParam: null,
  colorScheme: 'dark',
  isFullscreen: false,
  webApp: null,
});

export function useTelegram() {
  return useContext(TelegramContext);
}

interface TelegramProviderProps {
  children: ReactNode;
  enableFullscreen?: boolean;
}

export function TelegramProvider({
  children,
  enableFullscreen = true
}: TelegramProviderProps) {
  const [isReady, setIsReady] = useState(false);
  const [isTelegram, setIsTelegram] = useState(false);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [rawInitData, setRawInitData] = useState<string | null>(null);
  const [startParam, setStartParam] = useState<string | null>(null);
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>('dark');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [webApp, setWebApp] = useState<WebApp | null>(null);

  // CRITICAL: Flag to track fullscreen intent
  const isFullscreenIntentionalRef = useRef(false);
  // CRITICAL: Flag to prevent re-initialization
  const isInitializedRef = useRef(false);

  useEffect(() => {
    // Cleanup before re-initialization (Hot Reload)
    if (isInitializedRef.current && window.Telegram?.WebApp) {
      const WebApp = window.Telegram.WebApp;
      console.log('[TelegramProvider] Cleanup before re-init');

      if (WebApp.MainButton) {
        WebApp.MainButton.hide();
        WebApp.MainButton.offClick();
      }
      if (WebApp.SecondaryButton) {
        WebApp.SecondaryButton.hide();
        WebApp.SecondaryButton.offClick();
      }
      if (WebApp.BackButton) {
        WebApp.BackButton.hide();
        WebApp.BackButton.offClick();
      }
      if (WebApp.SettingsButton) {
        WebApp.SettingsButton.hide();
        WebApp.SettingsButton.offClick();
      }
      isInitializedRef.current = false;
    }

    const initTelegramApp = () => {
      try {
        // Check environment using URL params (more reliable than SDK)
        const isMiniApp = isTelegramMiniApp();

        if (!isMiniApp) {
          console.log('[TelegramProvider] Web browser detected (not Telegram)');
          setIsTelegram(false);
          setUser(MOCK_USER);
          setRawInitData('mock_init_data_for_development');
          setIsReady(true);
          isInitializedRef.current = true;
          return;
        }

        console.log('[TelegramProvider] Telegram Mini App environment detected');
        setIsTelegram(true);

        // After <Script strategy="beforeInteractive">, SDK is available SYNCHRONOUSLY
        if (!window.Telegram?.WebApp) {
          console.error('[TelegramProvider] Telegram SDK not loaded');
          setUser(MOCK_USER);
          setRawInitData('mock_init_data_for_development');
          setIsReady(true);
          isInitializedRef.current = true;
          return;
        }

        console.log('[TelegramProvider] Telegram SDK available');
        const WebApp = window.Telegram.WebApp;

        // ═══════════════════════════════════════════════════════════
        // STEP 1: Basic initialization and readiness
        // ═══════════════════════════════════════════════════════════
        WebApp.ready();
        console.log('[TelegramProvider] WebApp.ready() called');

        // ═══════════════════════════════════════════════════════════
        // STEP 2: Get init data
        // ═══════════════════════════════════════════════════════════
        const initDataRaw = WebApp.initData;
        const initDataUnsafe = WebApp.initDataUnsafe;

        console.log('[TelegramProvider] initData:', initDataRaw ? 'present' : 'missing');

        if (initDataRaw) {
          setRawInitData(initDataRaw);
        }

        if (initDataUnsafe?.user) {
          setUser(initDataUnsafe.user);
        }

        // Extract start_param for referral code (from t.me/bot?startapp=ref_CODE)
        if (initDataUnsafe?.start_param) {
          const param = initDataUnsafe.start_param;
          // Remove "ref_" prefix if present
          const refCode = param.startsWith('ref_') ? param.slice(4) : param;
          setStartParam(refCode);
          console.log('[TelegramProvider] Referral code extracted:', refCode);
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 3: Configure viewport
        // Sequence: expand() → requestFullscreen()
        // ═══════════════════════════════════════════════════════════
        if (WebApp.expand) {
          WebApp.expand();
          console.log('[TelegramProvider] App expanded');
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 4: Fullscreen with proper event handling
        // ═══════════════════════════════════════════════════════════
        WebApp.onEvent('fullscreenChanged', (event: any) => {
          const isFs = event?.isFullscreen ?? WebApp.isFullscreen;
          console.log(`[TelegramProvider] Fullscreen changed: ${isFs}`);
          setIsFullscreen(isFs);

          if (!isFs && !isFullscreenIntentionalRef.current) {
            console.log('[TelegramProvider] User exited fullscreen - respecting choice');
          }
          isFullscreenIntentionalRef.current = false;
        });

        WebApp.onEvent('fullscreenFailed', (event: any) => {
          const error = event?.error ?? 'UNKNOWN';
          console.warn(`[TelegramProvider] Fullscreen failed: ${error}`);
          isFullscreenIntentionalRef.current = false;
        });

        // Request fullscreen if enabled
        if (enableFullscreen && WebApp.requestFullscreen) {
          try {
            isFullscreenIntentionalRef.current = true;
            WebApp.requestFullscreen();
            console.log('[TelegramProvider] Fullscreen requested');
          } catch (error) {
            console.warn('[TelegramProvider] Fullscreen not available:', error);
            isFullscreenIntentionalRef.current = false;
          }
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 5: Request write access for bot messaging
        // ═══════════════════════════════════════════════════════════

        // Check if bot already has permission to write
        const allowsWriteToPm = initDataUnsafe?.user?.allows_write_to_pm;
        console.log('[TelegramProvider] allows_write_to_pm:', allowsWriteToPm);

        // If no permission yet, request it (shows native Telegram popup)
        if (!allowsWriteToPm && WebApp.requestWriteAccess) {
          WebApp.requestWriteAccess((granted) => {
            console.log('[TelegramProvider] Write access granted:', granted);
          });
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 6: Security and UX settings
        // ═══════════════════════════════════════════════════════════

        // Disable vertical swipes to close (Bot API 7.7+)
        if (WebApp.disableVerticalSwipes) {
          WebApp.disableVerticalSwipes();
          console.log('[TelegramProvider] Vertical swipes disabled');
        }

        // Enable closing confirmation (with desktop fullscreen exception)
        const isDesktop = ['tdesktop', 'macos', 'weba', 'webk', 'unigram'].includes(WebApp.platform);

        if (WebApp.enableClosingConfirmation) {
          if (!(isDesktop && enableFullscreen)) {
            WebApp.enableClosingConfirmation();
            console.log('[TelegramProvider] Closing confirmation enabled');
          }
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 7: Theme and colors
        // ═══════════════════════════════════════════════════════════
        const scheme = WebApp.colorScheme || 'dark';
        setColorScheme(scheme);

        // Set header/bottom bar to match our dark theme
        // Note: We don't call setBackgroundColor to allow CSS background image to show
        if (WebApp.setHeaderColor) {
          WebApp.setHeaderColor('#050712');
        }

        if (WebApp.setBottomBarColor) {
          WebApp.setBottomBarColor('#050712');
        }

        // Apply theme params to CSS variables
        const themeParams = WebApp.themeParams;
        if (themeParams) {
          const root = document.documentElement;

          if (themeParams.bg_color) {
            root.style.setProperty('--tg-theme-bg-color', themeParams.bg_color);
          }
          if (themeParams.text_color) {
            root.style.setProperty('--tg-theme-text-color', themeParams.text_color);
          }
          if (themeParams.hint_color) {
            root.style.setProperty('--tg-theme-hint-color', themeParams.hint_color);
          }
          if (themeParams.link_color) {
            root.style.setProperty('--tg-theme-link-color', themeParams.link_color);
          }
          if (themeParams.button_color) {
            root.style.setProperty('--tg-theme-button-color', themeParams.button_color);
          }
          if (themeParams.button_text_color) {
            root.style.setProperty('--tg-theme-button-text-color', themeParams.button_text_color);
          }
          if (themeParams.secondary_bg_color) {
            root.style.setProperty('--tg-theme-secondary-bg-color', themeParams.secondary_bg_color);
          }
          console.log('[TelegramProvider] Theme params applied to CSS');
        }

        // ═══════════════════════════════════════════════════════════
        // STEP 8: Safe Area Insets for iOS notch
        // ═══════════════════════════════════════════════════════════
        const updateSafeAreaInsets = () => {
          const root = document.documentElement;

          if (WebApp.safeAreaInset) {
            const { top, bottom, left, right } = WebApp.safeAreaInset;
            root.style.setProperty('--tg-safe-area-inset-top', `${top}px`);
            root.style.setProperty('--tg-safe-area-inset-bottom', `${bottom}px`);
            root.style.setProperty('--tg-safe-area-inset-left', `${left}px`);
            root.style.setProperty('--tg-safe-area-inset-right', `${right}px`);
          }

          if (WebApp.contentSafeAreaInset) {
            const { top, bottom, left, right } = WebApp.contentSafeAreaInset;
            root.style.setProperty('--tg-content-safe-area-inset-top', `${top}px`);
            root.style.setProperty('--tg-content-safe-area-inset-bottom', `${bottom}px`);
            root.style.setProperty('--tg-content-safe-area-inset-left', `${left}px`);
            root.style.setProperty('--tg-content-safe-area-inset-right', `${right}px`);
          }
        };

        updateSafeAreaInsets();

        WebApp.onEvent('safeAreaChanged', updateSafeAreaInsets);
        WebApp.onEvent('contentSafeAreaChanged', updateSafeAreaInsets);

        // ═══════════════════════════════════════════════════════════
        // STEP 9: Log app info
        // ═══════════════════════════════════════════════════════════
        console.log('[TelegramProvider] WebApp Info:', {
          version: WebApp.version,
          platform: WebApp.platform,
          colorScheme: WebApp.colorScheme,
          viewportHeight: WebApp.viewportHeight,
          viewportStableHeight: WebApp.viewportStableHeight,
          isExpanded: WebApp.isExpanded,
          isFullscreen: WebApp.isFullscreen,
        });

        // ═══════════════════════════════════════════════════════════
        // STEP 10: Block page scroll (prevent swipe-down close)
        // ═══════════════════════════════════════════════════════════
        document.body.classList.add('mobile-body');

        // ═══════════════════════════════════════════════════════════
        // STEP 11: Complete initialization
        // ═══════════════════════════════════════════════════════════
        setWebApp(WebApp);
        setIsReady(true);
        isInitializedRef.current = true;

        console.log('[TelegramProvider] Telegram Mini App fully initialized!');

      } catch (error) {
        console.error('[TelegramProvider] Init error:', error);
        setUser(MOCK_USER);
        setRawInitData('mock_init_data_for_development');
        setIsReady(true);
      }
    };

    initTelegramApp();

    // Cleanup on unmount
    return () => {
      console.log('[TelegramProvider] Cleanup on unmount');

      if (isTelegram) {
        document.body.classList.remove('mobile-body');
      }

      if (window.Telegram?.WebApp) {
        const WebApp = window.Telegram.WebApp;

        if (WebApp.MainButton) {
          WebApp.MainButton.hide();
          WebApp.MainButton.offClick();
        }
        if (WebApp.SecondaryButton) {
          WebApp.SecondaryButton.hide();
          WebApp.SecondaryButton.offClick();
        }
        if (WebApp.BackButton) {
          WebApp.BackButton.hide();
          WebApp.BackButton.offClick();
        }
        if (WebApp.SettingsButton) {
          WebApp.SettingsButton.hide();
          WebApp.SettingsButton.offClick();
        }
      }

      setIsReady(false);
      setWebApp(null);
      isInitializedRef.current = false;
    };
    // Empty deps - run only once on mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <TelegramContext.Provider
      value={{
        isReady,
        isTelegram,
        user,
        rawInitData,
        startParam,
        colorScheme,
        isFullscreen,
        webApp,
      }}
    >
      {children}
    </TelegramContext.Provider>
  );
}
