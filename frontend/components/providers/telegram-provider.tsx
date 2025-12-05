'use client';

import { useEffect, useState, createContext, useContext, type ReactNode } from 'react';

// Mock user for development (only used outside Telegram)
const MOCK_USER = {
  id: 123456789,
  firstName: 'Dev',
  lastName: 'User',
  username: 'devuser',
  languageCode: 'en',
  isPremium: false,
  allowsWriteToPm: true,
};

interface TelegramUser {
  id: number;
  firstName: string;
  lastName?: string;
  username?: string;
  languageCode?: string;
  isPremium?: boolean;
  allowsWriteToPm?: boolean;
}

interface TelegramContextValue {
  isReady: boolean;
  isTelegram: boolean;
  user: TelegramUser | null;
  rawInitData: string | null;
  colorScheme: 'light' | 'dark';
  isFullscreen: boolean;
}

const TelegramContext = createContext<TelegramContextValue>({
  isReady: false,
  isTelegram: false,
  user: null,
  rawInitData: null,
  colorScheme: 'dark',
  isFullscreen: false,
});

export function useTelegram() {
  return useContext(TelegramContext);
}

interface TelegramProviderProps {
  children: ReactNode;
}

export function TelegramProvider({ children }: TelegramProviderProps) {
  const [isReady, setIsReady] = useState(false);
  const [isTelegram, setIsTelegram] = useState(false);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [rawInitData, setRawInitData] = useState<string | null>(null);
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>('dark');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    const initTelegram = async () => {
      try {
        // Check if we're in Telegram by looking for WebApp object
        const webApp = typeof window !== 'undefined'
          ? (window as any).Telegram?.WebApp
          : null;

        const isTg = !!webApp;
        setIsTelegram(isTg);
        console.log('[TelegramProvider] isTelegram:', isTg);

        if (!isTg) {
          // Dev mode - use mock data
          console.log('[TelegramProvider] Not in Telegram, using mock mode');
          setUser(MOCK_USER);
          setRawInitData('mock_init_data_for_development');
          setIsReady(true);
          return;
        }

        // Get init data directly from WebApp object (most reliable way)
        const initDataRaw = webApp.initData;
        const initDataUnsafe = webApp.initDataUnsafe;

        console.log('[TelegramProvider] initData:', initDataRaw);
        console.log('[TelegramProvider] initDataUnsafe:', initDataUnsafe);

        if (initDataRaw) {
          setRawInitData(initDataRaw);
        }

        // Set user from initDataUnsafe
        if (initDataUnsafe?.user) {
          const tgUser = initDataUnsafe.user;
          setUser({
            id: tgUser.id,
            firstName: tgUser.first_name,
            lastName: tgUser.last_name,
            username: tgUser.username,
            languageCode: tgUser.language_code,
            isPremium: tgUser.is_premium,
            allowsWriteToPm: tgUser.allows_write_to_pm,
          });
        }

        // Get color scheme from WebApp
        const scheme = webApp.colorScheme || 'dark';
        setColorScheme(scheme);

        // Tell Telegram we're ready
        webApp.ready();

        // Expand to full height
        webApp.expand();

        // Try to use SDK for additional features
        try {
          const {
            init,
            viewport,
            themeParams,
            swipeBehavior,
            miniApp,
          } = await import('@telegram-apps/sdk-react');

          init({ acceptCustomStyles: true });

          // Configure viewport
          if (viewport.mount.isAvailable()) {
            await viewport.mount();

            if (viewport.requestFullscreen.isAvailable()) {
              try {
                await viewport.requestFullscreen();
                setIsFullscreen(true);
              } catch (err) {
                console.warn('[TelegramProvider] Fullscreen not available:', err);
              }
            }

            if (viewport.bindCssVars.isAvailable()) {
              viewport.bindCssVars();
            }
          }

          // Disable vertical swipe to close
          if (swipeBehavior.mount.isAvailable()) {
            swipeBehavior.mount();
            if (swipeBehavior.disableVertical.isAvailable()) {
              swipeBehavior.disableVertical();
            }
          }

          // Bind theme CSS variables
          if (themeParams.bindCssVars.isAvailable()) {
            themeParams.bindCssVars();
          }

          if (miniApp.bindCssVars.isAvailable()) {
            miniApp.bindCssVars();
          }
        } catch (sdkError) {
          console.warn('[TelegramProvider] SDK features error:', sdkError);
          // SDK features are optional, continue without them
        }

        setIsReady(true);
      } catch (error) {
        console.error('[TelegramProvider] Init error:', error);
        // Fallback to mock mode on error
        setUser(MOCK_USER);
        setRawInitData('mock_init_data_for_development');
        setIsReady(true);
      }
    };

    initTelegram();
  }, []);

  return (
    <TelegramContext.Provider
      value={{
        isReady,
        isTelegram,
        user,
        rawInitData,
        colorScheme,
        isFullscreen,
      }}
    >
      {children}
    </TelegramContext.Provider>
  );
}
