'use client';

import { useCallback, useRef } from 'react';

type ImpactStyle = 'light' | 'medium' | 'heavy' | 'rigid' | 'soft';
type NotificationType = 'success' | 'error' | 'warning';

interface HapticFeedbackAPI {
  impactOccurred: (style: ImpactStyle) => void;
  notificationOccurred: (type: NotificationType) => void;
  selectionChanged: () => void;
}

// Cached SDK imports
let hapticFeedbackModule: HapticFeedbackAPI | null = null;
let isLoadingModule = false;
let loadPromise: Promise<void> | null = null;

async function loadHapticModule(): Promise<HapticFeedbackAPI | null> {
  if (hapticFeedbackModule) return hapticFeedbackModule;
  if (isLoadingModule && loadPromise) {
    await loadPromise;
    return hapticFeedbackModule;
  }

  isLoadingModule = true;
  loadPromise = (async () => {
    try {
      const sdk = await import('@telegram-apps/sdk-react');
      const { hapticFeedback } = sdk;

      hapticFeedbackModule = {
        impactOccurred: (style: ImpactStyle) => {
          if (hapticFeedback.impactOccurred.isAvailable()) {
            hapticFeedback.impactOccurred(style);
          }
        },
        notificationOccurred: (type: NotificationType) => {
          if (hapticFeedback.notificationOccurred.isAvailable()) {
            hapticFeedback.notificationOccurred(type);
          }
        },
        selectionChanged: () => {
          if (hapticFeedback.selectionChanged.isAvailable()) {
            hapticFeedback.selectionChanged();
          }
        },
      };
    } catch (error) {
      console.warn('[Haptic] Failed to load SDK:', error);
      hapticFeedbackModule = null;
    }
  })();

  await loadPromise;
  isLoadingModule = false;
  return hapticFeedbackModule;
}

export function useHaptic() {
  const moduleRef = useRef<HapticFeedbackAPI | null>(null);

  // Initialize module on first use
  const ensureModule = useCallback(async () => {
    if (!moduleRef.current) {
      moduleRef.current = await loadHapticModule();
    }
    return moduleRef.current;
  }, []);

  // Impact feedback - for button presses, collisions
  const impact = useCallback(
    async (style: ImpactStyle = 'medium') => {
      const module = await ensureModule();
      module?.impactOccurred(style);
    },
    [ensureModule]
  );

  // Notification feedback - for success/error/warning states
  const notification = useCallback(
    async (type: NotificationType) => {
      const module = await ensureModule();
      module?.notificationOccurred(type);
    },
    [ensureModule]
  );

  // Selection feedback - for scrolling, selection changes
  const selection = useCallback(async () => {
    const module = await ensureModule();
    module?.selectionChanged();
  }, [ensureModule]);

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
let globalHaptic: ReturnType<typeof useHaptic> | null = null;

export function getHaptic() {
  if (!globalHaptic) {
    const ensureModule = async () => {
      return await loadHapticModule();
    };

    globalHaptic = {
      impact: async (style: ImpactStyle = 'medium') => {
        const module = await ensureModule();
        module?.impactOccurred(style);
      },
      notification: async (type: NotificationType) => {
        const module = await ensureModule();
        module?.notificationOccurred(type);
      },
      selection: async () => {
        const module = await ensureModule();
        module?.selectionChanged();
      },
      tap: async () => {
        const module = await ensureModule();
        module?.impactOccurred('light');
      },
      press: async () => {
        const module = await ensureModule();
        module?.impactOccurred('medium');
      },
      heavyPress: async () => {
        const module = await ensureModule();
        module?.impactOccurred('heavy');
      },
      success: async () => {
        const module = await ensureModule();
        module?.notificationOccurred('success');
      },
      error: async () => {
        const module = await ensureModule();
        module?.notificationOccurred('error');
      },
      warning: async () => {
        const module = await ensureModule();
        module?.notificationOccurred('warning');
      },
    };
  }
  return globalHaptic;
}
