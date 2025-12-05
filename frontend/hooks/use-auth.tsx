'use client';

import {
  useState,
  useEffect,
  useCallback,
  createContext,
  useContext,
  type ReactNode,
} from 'react';
import { authApi, setAuthToken, getAuthToken, setRefreshTokenHandler } from '@/lib/api';
import { useTelegram } from '@/components/providers/telegram-provider';
import type { User } from '@/types/api';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: () => Promise<boolean>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  error: null,
  login: async () => false,
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { isReady, isTelegram, rawInitData, startParam } = useTelegram();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (): Promise<boolean> => {
    if (!rawInitData && isTelegram) {
      setError('No Telegram init data');
      setIsLoading(false);
      return false;
    }

    try {
      setIsLoading(true);
      setError(null);

      const initData = rawInitData || 'mock_init_data_for_development';
      // Pass referral code from startapp URL param
      const response = await authApi.loginTelegram(initData, startParam);
      setAuthToken(response.access_token);
      setUser(response.user);
      return true;
    } catch (err) {
      console.error('[Auth] Login failed:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [rawInitData, isTelegram, startParam]);

  // Register refresh token handler
  useEffect(() => {
    setRefreshTokenHandler(async () => {
      console.log('[Auth] Refreshing token via re-login...');
      return login();
    });

    return () => {
      setRefreshTokenHandler(null);
    };
  }, [login]);

  const logout = useCallback(() => {
    setAuthToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const userData = await authApi.me();
          setUser(userData);
          setIsLoading(false);
          return;
        } catch {
          // Token expired or invalid - clear it
          setAuthToken(null);
        }
      }

      // No valid token - try to login if we have initData
      if (rawInitData) {
        await login();
      } else {
        setIsLoading(false);
      }
    };

    if (isReady) {
      checkAuth();
    }
  }, [isReady, rawInitData, login]);

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: !!user,
    error,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
