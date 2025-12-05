'use client';

import { useCallback } from 'react';

type ImpactStyle = 'light' | 'medium' | 'heavy' | 'rigid' | 'soft';
type NotificationType = 'success' | 'error' | 'warning';

function getWebApp() {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
    return window.Telegram.WebApp;
  }
  return null;
}

export function useHaptic() {
  // Impact feedback - for button presses, collisions
  const impact = useCallback((style: ImpactStyle = 'medium') => {
    try {
      const webApp = getWebApp();
      if (webApp?.HapticFeedback?.impactOccurred) {
        webApp.HapticFeedback.impactOccurred(style);
      }
    } catch (e) {
      // Silently ignore haptic errors
    }
  }, []);

  // Notification feedback - for success/error/warning states
  const notification = useCallback((type: NotificationType) => {
    try {
      const webApp = getWebApp();
      if (webApp?.HapticFeedback?.notificationOccurred) {
        webApp.HapticFeedback.notificationOccurred(type);
      }
    } catch (e) {
      // Silently ignore haptic errors
    }
  }, []);

  // Selection feedback - for scrolling, selection changes
  const selection = useCallback(() => {
    try {
      const webApp = getWebApp();
      if (webApp?.HapticFeedback?.selectionChanged) {
        webApp.HapticFeedback.selectionChanged();
      }
    } catch (e) {
      // Silently ignore haptic errors
    }
  }, []);

  // Convenient presets
  const tap = useCallback(() => impact('light'), [impact]);
  const press = useCallback(() => impact('medium'), [impact]);
  const heavyPress = useCallback(() => impact('heavy'), [impact]);
  const success = useCallback(() => notification('success'), [notification]);
  const error = useCallback(() => notification('error'), [notification]);
  const warning = useCallback(() => notification('warning'), [notification]);

  return {
    // Core methods
    impact,
    notification,
    selection,
    // Presets
    tap,
    press,
    heavyPress,
    success,
    error,
    warning,
  };
}

// Singleton for non-hook usage
export function getHaptic() {
  const webApp = getWebApp();

  return {
    impact: (style: ImpactStyle = 'medium') => {
      try {
        webApp?.HapticFeedback?.impactOccurred?.(style);
      } catch (e) {}
    },
    notification: (type: NotificationType) => {
      try {
        webApp?.HapticFeedback?.notificationOccurred?.(type);
      } catch (e) {}
    },
    selection: () => {
      try {
        webApp?.HapticFeedback?.selectionChanged?.();
      } catch (e) {}
    },
    tap: () => {
      try {
        webApp?.HapticFeedback?.impactOccurred?.('light');
      } catch (e) {}
    },
    press: () => {
      try {
        webApp?.HapticFeedback?.impactOccurred?.('medium');
      } catch (e) {}
    },
    heavyPress: () => {
      try {
        webApp?.HapticFeedback?.impactOccurred?.('heavy');
      } catch (e) {}
    },
    success: () => {
      try {
        webApp?.HapticFeedback?.notificationOccurred?.('success');
      } catch (e) {}
    },
    error: () => {
      try {
        webApp?.HapticFeedback?.notificationOccurred?.('error');
      } catch (e) {}
    },
    warning: () => {
      try {
        webApp?.HapticFeedback?.notificationOccurred?.('warning');
      } catch (e) {}
    },
  };
}
