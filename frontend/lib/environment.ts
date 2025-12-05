/**
 * Environment detection utilities for Telegram Mini App
 *
 * IMPORTANT: These functions do NOT depend on Telegram SDK loading!
 * They use URL parameters and other signals available immediately.
 */

/**
 * Determines if the app is running inside Telegram Mini App
 * @returns true if running in Telegram, false if in a regular browser
 */
export function isTelegramMiniApp(): boolean {
  if (typeof window === 'undefined') return false;

  // 1. Check URL parameters - most reliable method
  // Telegram always adds special parameters to Mini App URLs
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const hash = window.location.hash;

    // Check for Telegram-specific parameters
    if (
      urlParams.has('tgWebAppPlatform') ||
      urlParams.has('tgWebAppVersion') ||
      urlParams.has('tgWebAppStartParam') ||
      hash.includes('tgWebAppData=')
    ) {
      return true;
    }
  } catch (e) {
    console.warn('[Environment] Error checking URL params:', e);
  }

  // 2. Check user agent - fallback method
  const userAgent = window.navigator.userAgent.toLowerCase();
  if (userAgent.includes('telegram')) {
    return true;
  }

  // 3. Check for global Telegram object (not its properties!)
  // This object is created immediately, before full SDK initialization
  if (typeof (window as any).Telegram !== 'undefined') {
    return true;
  }

  return false;
}

/**
 * Determines if the app is running in a regular web browser
 * @returns true if running in browser (not in Telegram)
 */
export function isWebBrowser(): boolean {
  return !isTelegramMiniApp();
}

/**
 * Returns the environment type
 * @returns 'miniapp' for Telegram Mini App, 'web' for regular browser
 */
export function getEnvironment(): 'miniapp' | 'web' {
  return isTelegramMiniApp() ? 'miniapp' : 'web';
}
