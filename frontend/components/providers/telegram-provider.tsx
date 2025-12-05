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
        // Import bridge to check if we're in Telegram
        const { isTMA, retrieveLaunchParams, retrieveRawInitData } = await import('@telegram-apps/bridge');

        const isTg = isTMA();
        setIsTelegram(isTg);

        if (!isTg) {
          // Dev mode - use mock data
          console.log('[TelegramProvider] Not in Telegram, using mock mode');
          setUser(MOCK_USER);
          setRawInitData('mock_init_data_for_development');
          setIsReady(true);
          return;
        }

        // Get launch params (contains initData)
        const launchParams = retrieveLaunchParams(true); // true = camelCase keys
        console.log('[TelegramProvider] Launch params:', launchParams);

        // Set raw init data for auth (use dedicated function)
        const rawInitData = retrieveRawInitData();
        if (rawInitData) {
          setRawInitData(rawInitData);
        }

        // Set user from init data (tgWebAppData in v2)
        const tgWebAppData = (launchParams as any).tgWebAppData;
        if (tgWebAppData?.user) {
          const tgUser = tgWebAppData.user;
          setUser({
            id: tgUser.id,
            firstName: tgUser.first_name || tgUser.firstName,
            lastName: tgUser.last_name || tgUser.lastName,
            username: tgUser.username,
            languageCode: tgUser.language_code || tgUser.languageCode,
            isPremium: tgUser.is_premium || tgUser.isPremium,
            allowsWriteToPm: tgUser.allows_write_to_pm || tgUser.allowsWriteToPm,
          });
        }

        // Import SDK for UI features
        const {
          init,
          miniApp,
          viewport,
          themeParams,
          swipeBehavior,
        } = await import('@telegram-apps/sdk-react');

        // Initialize SDK
        init({ acceptCustomStyles: true });

        // Configure viewport
        if (viewport.mount.isAvailable()) {
          await viewport.mount();

          if (viewport.expand.isAvailable()) {
            viewport.expand();
          }

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

        // Get color scheme
        const scheme = miniApp.isDark?.() ? 'dark' : 'light';
        setColorScheme(scheme);

        // Notify Telegram we're ready
        if (miniApp.ready.isAvailable()) {
          miniApp.ready();
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
