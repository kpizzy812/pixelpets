/**
 * Mock Telegram environment for development outside Telegram
 */

export const MOCK_USER = {
  id: 123456789,
  firstName: 'Dev',
  lastName: 'User',
  username: 'devuser',
  languageCode: 'en',
  isPremium: false,
};

export const MOCK_INIT_DATA = 'mock_init_data_for_development';

export function setupTelegramMock() {
  if (typeof window === 'undefined') return;
  if ((window as any).Telegram?.WebApp) return; // Already in Telegram

  console.log('[TelegramMock] Setting up mock environment');

  (window as any).Telegram = {
    WebApp: {
      initData: MOCK_INIT_DATA,
      initDataUnsafe: {
        user: MOCK_USER,
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'mock_hash',
      },
      version: '7.0',
      platform: 'web',
      colorScheme: 'dark',
      themeParams: {
        bg_color: '#050712',
        text_color: '#f1f5f9',
        hint_color: '#64748b',
        link_color: '#00f5d4',
        button_color: '#c7f464',
        button_text_color: '#050712',
        secondary_bg_color: '#0d1220',
      },
      isExpanded: true,
      viewportHeight: 844,
      viewportStableHeight: 844,
      ready: () => console.log('[TelegramMock] ready()'),
      expand: () => console.log('[TelegramMock] expand()'),
      close: () => console.log('[TelegramMock] close()'),
      MainButton: {
        text: '',
        color: '#c7f464',
        textColor: '#050712',
        isVisible: false,
        isActive: true,
        isProgressVisible: false,
        setText: (text: string) => console.log('[TelegramMock] MainButton.setText:', text),
        show: () => console.log('[TelegramMock] MainButton.show()'),
        hide: () => console.log('[TelegramMock] MainButton.hide()'),
        onClick: () => {},
        offClick: () => {},
      },
      BackButton: {
        isVisible: false,
        show: () => console.log('[TelegramMock] BackButton.show()'),
        hide: () => console.log('[TelegramMock] BackButton.hide()'),
        onClick: () => {},
        offClick: () => {},
      },
      HapticFeedback: {
        impactOccurred: (style: string) => console.log('[TelegramMock] haptic:', style),
        notificationOccurred: (type: string) => console.log('[TelegramMock] notification:', type),
        selectionChanged: () => console.log('[TelegramMock] selectionChanged'),
      },
    },
  };
}
