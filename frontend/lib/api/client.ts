/**
 * API Client - fetch wrapper with JWT auth and automatic token refresh
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type RequestMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions {
  method?: RequestMethod;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string | null;
  skipAuthRefresh?: boolean; // Prevent infinite refresh loop
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data: unknown
  ) {
    super(`API Error: ${status} ${statusText}`);
    this.name = 'ApiError';
  }
}

// Token storage (client-side only)
let authToken: string | null = null;

// Refresh token handler - will be set by AuthProvider
let refreshTokenHandler: (() => Promise<boolean>) | null = null;
let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

export function setRefreshTokenHandler(handler: (() => Promise<boolean>) | null) {
  refreshTokenHandler = handler;
}

export function setAuthToken(token: string | null) {
  authToken = token;
  if (typeof window !== 'undefined') {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export function getAuthToken(): string | null {
  if (authToken) return authToken;
  if (typeof window !== 'undefined') {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

// Attempt to refresh the token
async function tryRefreshToken(): Promise<boolean> {
  if (!refreshTokenHandler) {
    console.warn('[API] No refresh token handler registered');
    return false;
  }

  // If already refreshing, wait for that to complete
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = refreshTokenHandler()
    .then((success) => {
      console.log('[API] Token refresh:', success ? 'success' : 'failed');
      return success;
    })
    .catch((err) => {
      console.error('[API] Token refresh error:', err);
      return false;
    })
    .finally(() => {
      isRefreshing = false;
      refreshPromise = null;
    });

  return refreshPromise;
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {}, token, skipAuthRefresh = false } = options;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  // Add auth token
  const authHeader = token ?? getAuthToken();
  if (authHeader) {
    requestHeaders['Authorization'] = `Bearer ${authHeader}`;
  }

  const config: RequestInit = {
    method,
    headers: requestHeaders,
  };

  if (body && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, config);

  // Handle non-JSON responses
  const contentType = response.headers.get('content-type');
  const isJson = contentType?.includes('application/json');

  // Handle 401 - try to refresh token
  if (response.status === 401 && !skipAuthRefresh) {
    console.log('[API] Got 401, attempting token refresh...');
    const refreshed = await tryRefreshToken();

    if (refreshed) {
      // Retry the request with the new token
      return apiRequest<T>(endpoint, { ...options, skipAuthRefresh: true });
    }

    // Refresh failed, clear token and throw
    setAuthToken(null);
    const errorData = isJson ? await response.json() : await response.text();
    throw new ApiError(response.status, response.statusText, errorData);
  }

  if (!response.ok) {
    const errorData = isJson ? await response.json() : await response.text();
    throw new ApiError(response.status, response.statusText, errorData);
  }

  if (response.status === 204 || !isJson) {
    return null as T;
  }

  return response.json();
}

// Shorthand methods
export const api = {
  get: <T>(endpoint: string, token?: string) =>
    apiRequest<T>(endpoint, { method: 'GET', token }),

  post: <T>(endpoint: string, body?: unknown, token?: string) =>
    apiRequest<T>(endpoint, { method: 'POST', body, token }),

  put: <T>(endpoint: string, body?: unknown, token?: string) =>
    apiRequest<T>(endpoint, { method: 'PUT', body, token }),

  patch: <T>(endpoint: string, body?: unknown, token?: string) =>
    apiRequest<T>(endpoint, { method: 'PATCH', body, token }),

  delete: <T>(endpoint: string, token?: string) =>
    apiRequest<T>(endpoint, { method: 'DELETE', token }),
};
