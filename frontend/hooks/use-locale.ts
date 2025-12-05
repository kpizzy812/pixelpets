'use client';

import { useCallback } from 'react';
import { useLocale as useNextIntlLocale } from 'next-intl';
import type { Locale } from '@/i18n/request';

export function useLocale() {
  const locale = useNextIntlLocale() as Locale;

  const setLocale = useCallback((newLocale: Locale) => {
    // Set cookie for server-side locale detection
    document.cookie = `locale=${newLocale};path=/;max-age=${60 * 60 * 24 * 365}`;
    // Reload to apply new locale
    window.location.reload();
  }, []);

  return { locale, setLocale };
}
