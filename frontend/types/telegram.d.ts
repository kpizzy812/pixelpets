/**
 * Telegram Web App API Types
 *
 * Extends the global Window interface for Telegram Mini Apps support
 * @see https://core.telegram.org/bots/webapps
 */

export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
  is_premium?: boolean;
  allows_write_to_pm?: boolean;
  photo_url?: string;
}

export interface ThemeParams {
  bg_color?: string;
  text_color?: string;
  hint_color?: string;
  link_color?: string;
  button_color?: string;
  button_text_color?: string;
  secondary_bg_color?: string;
  header_bg_color?: string;
  bottom_bar_bg_color?: string;
  accent_text_color?: string;
  section_bg_color?: string;
  section_header_text_color?: string;
  subtitle_text_color?: string;
  destructive_text_color?: string;
}

export interface SafeAreaInset {
  top: number;
  bottom: number;
  left: number;
  right: number;
}

export interface MainButton {
  text: string;
  color: string;
  textColor: string;
  isVisible: boolean;
  isActive: boolean;
  isProgressVisible: boolean;
  setText: (text: string) => MainButton;
  onClick: (callback: VoidFunction) => MainButton;
  offClick: (callback?: VoidFunction) => MainButton;
  show: () => MainButton;
  hide: () => MainButton;
  enable: () => MainButton;
  disable: () => MainButton;
  showProgress: (leaveActive?: boolean) => MainButton;
  hideProgress: () => MainButton;
  setParams: (params: {
    text?: string;
    color?: string;
    text_color?: string;
    is_active?: boolean;
    is_visible?: boolean;
  }) => MainButton;
}

export interface SecondaryButton extends MainButton {
  position: 'left' | 'right' | 'top' | 'bottom';
  setParams: (params: {
    text?: string;
    color?: string;
    text_color?: string;
    is_active?: boolean;
    is_visible?: boolean;
    position?: 'left' | 'right' | 'top' | 'bottom';
  }) => SecondaryButton;
}

export interface BackButton {
  isVisible: boolean;
  onClick: (callback: VoidFunction) => BackButton;
  offClick: (callback?: VoidFunction) => BackButton;
  show: () => BackButton;
  hide: () => BackButton;
}

export interface SettingsButton {
  isVisible: boolean;
  onClick: (callback: VoidFunction) => SettingsButton;
  offClick: (callback?: VoidFunction) => SettingsButton;
  show: () => SettingsButton;
  hide: () => SettingsButton;
}

export interface HapticFeedback {
  impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => HapticFeedback;
  notificationOccurred: (type: 'error' | 'success' | 'warning') => HapticFeedback;
  selectionChanged: () => HapticFeedback;
}

export interface CloudStorage {
  setItem: (key: string, value: string, callback?: (error: Error | null, success: boolean) => void) => CloudStorage;
  getItem: (key: string, callback: (error: Error | null, value: string | null) => void) => CloudStorage;
  getItems: (keys: string[], callback: (error: Error | null, values: Record<string, string>) => void) => CloudStorage;
  removeItem: (key: string, callback?: (error: Error | null, success: boolean) => void) => CloudStorage;
  removeItems: (keys: string[], callback?: (error: Error | null, success: boolean) => void) => CloudStorage;
  getKeys: (callback: (error: Error | null, keys: string[]) => void) => CloudStorage;
}

export interface BiometricManager {
  isInited: boolean;
  isBiometricAvailable: boolean;
  biometricType: 'finger' | 'face' | 'unknown';
  isAccessRequested: boolean;
  isAccessGranted: boolean;
  isBiometricTokenSaved: boolean;
  deviceId: string;
  init: (callback?: VoidFunction) => BiometricManager;
  requestAccess: (params: { reason?: string }, callback?: (granted: boolean) => void) => BiometricManager;
  authenticate: (params: { reason?: string }, callback?: (success: boolean, token?: string) => void) => BiometricManager;
  updateBiometricToken: (token: string, callback?: (updated: boolean) => void) => BiometricManager;
  openSettings: () => BiometricManager;
}

export type WebAppEvent =
  | 'themeChanged'
  | 'viewportChanged'
  | 'mainButtonClicked'
  | 'secondaryButtonClicked'
  | 'backButtonClicked'
  | 'settingsButtonClicked'
  | 'invoiceClosed'
  | 'popupClosed'
  | 'qrTextReceived'
  | 'scanQrPopupClosed'
  | 'clipboardTextReceived'
  | 'writeAccessRequested'
  | 'contactRequested'
  | 'biometricManagerUpdated'
  | 'biometricAuthRequested'
  | 'biometricTokenUpdated'
  | 'fullscreenChanged'
  | 'fullscreenFailed'
  | 'homeScreenAdded'
  | 'homeScreenChecked'
  | 'accelerometerStarted'
  | 'accelerometerStopped'
  | 'accelerometerChanged'
  | 'accelerometerFailed'
  | 'deviceOrientationStarted'
  | 'deviceOrientationStopped'
  | 'deviceOrientationChanged'
  | 'deviceOrientationFailed'
  | 'gyroscopeStarted'
  | 'gyroscopeStopped'
  | 'gyroscopeChanged'
  | 'gyroscopeFailed'
  | 'locationManagerUpdated'
  | 'locationRequested'
  | 'shareMessageSent'
  | 'shareMessageFailed'
  | 'emojiStatusSet'
  | 'emojiStatusFailed'
  | 'emojiStatusAccessRequested'
  | 'fileDownloadRequested'
  | 'safeAreaChanged'
  | 'contentSafeAreaChanged';

export interface WebApp {
  // Properties
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: TelegramUser;
    receiver?: TelegramUser;
    chat?: {
      id: number;
      type: string;
      title?: string;
      username?: string;
      photo_url?: string;
    };
    chat_type?: string;
    chat_instance?: string;
    start_param?: string;
    can_send_after?: number;
    auth_date: number;
    hash: string;
  };
  version: string;
  platform: string;
  colorScheme: 'light' | 'dark';
  themeParams: ThemeParams;
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  bottomBarColor?: string;
  isClosingConfirmationEnabled: boolean;
  isVerticalSwipesEnabled: boolean;
  isFullscreen: boolean;
  isOrientationLocked: boolean;
  safeAreaInset?: SafeAreaInset;
  contentSafeAreaInset?: SafeAreaInset;

  // Components
  MainButton: MainButton;
  SecondaryButton?: SecondaryButton;
  BackButton: BackButton;
  SettingsButton?: SettingsButton;
  HapticFeedback: HapticFeedback;
  CloudStorage: CloudStorage;
  BiometricManager?: BiometricManager;

  // Methods
  ready: () => void;
  expand: () => void;
  close: () => void;
  enableClosingConfirmation: () => void;
  disableClosingConfirmation: () => void;
  enableVerticalSwipes: () => void;
  disableVerticalSwipes: () => void;
  requestFullscreen?: () => void;
  exitFullscreen?: () => void;
  lockOrientation?: () => void;
  unlockOrientation?: () => void;
  setHeaderColor: (color: 'bg_color' | 'secondary_bg_color' | string) => void;
  setBackgroundColor: (color: 'bg_color' | 'secondary_bg_color' | string) => void;
  setBottomBarColor?: (color: 'bg_color' | 'secondary_bg_color' | 'bottom_bar_bg_color' | string) => void;
  sendData: (data: string) => void;
  switchInlineQuery: (query: string, choose_chat_types?: string[]) => void;
  openLink: (url: string, options?: { try_instant_view?: boolean }) => void;
  openTelegramLink: (url: string) => void;
  openInvoice: (url: string, callback?: (status: string) => void) => void;
  shareToStory?: (media_url: string, params?: { text?: string; widget_link?: { url: string; name?: string } }) => void;
  showPopup: (params: {
    title?: string;
    message: string;
    buttons?: Array<{
      id?: string;
      type?: 'default' | 'ok' | 'close' | 'cancel' | 'destructive';
      text?: string;
    }>;
  }, callback?: (button_id: string) => void) => void;
  showAlert: (message: string, callback?: VoidFunction) => void;
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void;
  showScanQrPopup: (params?: { text?: string }, callback?: (text: string) => boolean | void) => void;
  closeScanQrPopup: () => void;
  readTextFromClipboard: (callback?: (text: string | null) => void) => void;
  requestWriteAccess: (callback?: (granted: boolean) => void) => void;
  requestContact: (callback?: (shared: boolean) => void) => void;

  // Events
  onEvent: (eventType: WebAppEvent, eventHandler: (event?: any) => void) => void;
  offEvent: (eventType: WebAppEvent, eventHandler: (event?: any) => void) => void;
}

export interface Telegram {
  WebApp: WebApp;
}

declare global {
  interface Window {
    Telegram?: Telegram;
  }
}

export {};
