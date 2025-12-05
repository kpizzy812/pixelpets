'use client';

import {
  useState,
  useEffect,
  useCallback,
  createContext,
  useContext,
  type ReactNode,
} from 'react';
import { authApi, setAuthToken, getAuthToken } from '@/lib/api';
import { useTelegram } from '@/components/providers/telegram-provider';
import type { User } from '@/types/api';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  error: null,
  login: async () => {},
  logout: () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { isReady, isTelegram, rawInitData } = useTelegram();
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async () => {
    if (!rawInitData && isTelegram) {
      setError('No Telegram init data');
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      const initData = rawInitData || 'mock_init_data_for_development';
      const response = await authApi.loginTelegram(initData);
      setAuthToken(response.access_token);
      setUser(response.user);
    } catch (err) {
      console.error('[Auth] Login failed:', err);
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  }, [rawInitData, isTelegram]);

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
        } catch {
          setAuthToken(null);
        }
      }
      setIsLoading(false);
    };

    if (isReady) {
      checkAuth();
    }
  }, [isReady]);

  useEffect(() => {
    if (isReady && !user && rawInitData) {
      login();
    }
  }, [isReady, user, rawInitData, login]);

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
