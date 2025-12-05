'use client';

import { useEffect, useState, createContext, useContext, type ReactNode } from 'react';
import { isTelegramWebApp } from '@/lib/telegram';

// Mock user for development
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
      const isTg = isTelegramWebApp();
      setIsTelegram(isTg);

      if (!isTg) {
        // Dev mode - use mock data
        console.log('[TelegramProvider] Not in Telegram, using mock mode');
        setUser(MOCK_USER);
        setRawInitData('mock_init_data_for_development');
        setIsReady(true);
        return;
      }

      try {
        // Dynamically import SDK only when in Telegram
        const {
          init,
          miniApp,
          viewport,
          themeParams,
          initData,
          swipeBehavior,
        } = await import('@telegram-apps/sdk-react');

        // Initialize SDK
        init({ acceptCustomStyles: true });

        // Mount components
        if (miniApp.mount.isAvailable()) {
          miniApp.mount();
        }

        // Mount and configure viewport
        if (viewport.mount.isAvailable()) {
          await viewport.mount();

          // 1. Expand viewport first
          if (viewport.expand.isAvailable()) {
            viewport.expand();
          }

          // 2. Request fullscreen mode
          if (viewport.requestFullscreen.isAvailable()) {
            try {
              await viewport.requestFullscreen();
              setIsFullscreen(true);
            } catch (err) {
              console.warn('[TelegramProvider] Fullscreen not available:', err);
            }
          }

          // 3. Bind CSS variables for viewport dimensions
          if (viewport.bindCssVars.isAvailable()) {
            viewport.bindCssVars();
          }
        }

        // Mount and disable vertical swipe to close
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

        // Get init data
        const data = initData.state();
        if (data) {
          const tgUser = data.user;
          if (tgUser) {
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
          setRawInitData(initData.raw() ?? null);
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
