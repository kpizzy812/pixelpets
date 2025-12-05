/**
 * Telegram Mini App utilities
 */

// Check if running inside Telegram WebApp
export function isTelegramWebApp(): boolean {
  if (typeof window === 'undefined') return false;
  return !!(window as any).Telegram?.WebApp;
}

// Get raw Telegram WebApp object
export function getTelegramWebApp() {
  if (typeof window === 'undefined') return null;
  return (window as any).Telegram?.WebApp ?? null;
}
