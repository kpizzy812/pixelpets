'use client';

import { useTranslations } from 'next-intl';
import { PageLayout } from '@/components/layout/page-layout';
import { useGameStore } from '@/store/game-store';
import { useHaptic } from '@/hooks/use-haptic';
import { useLocale } from '@/hooks/use-locale';
import type { Locale } from '@/i18n/request';

interface LanguageOption {
  code: Locale;
  nativeName: string;
}

const LANGUAGES: LanguageOption[] = [
  { code: 'en', nativeName: 'English' },
  { code: 'ru', nativeName: 'Русский' },
  { code: 'de', nativeName: 'Deutsch' },
  { code: 'es', nativeName: 'Español' },
  { code: 'fr', nativeName: 'Français' },
  { code: 'pt', nativeName: 'Português' },
  { code: 'it', nativeName: 'Italiano' },
];

export function SettingsScreen() {
  const { user } = useGameStore();
  const { locale, setLocale } = useLocale();
  const { selection, success } = useHaptic();
  const t = useTranslations('settings');

  const handleLanguageChange = (lang: Locale) => {
    if (lang === locale) return;
    selection();
    setLocale(lang);
    success();
  };

  return (
    <PageLayout title={t('title')}>
      <div className="p-4 space-y-6">
        {/* User Info */}
        {user && (
          <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#00f5d4] to-[#c7f464] flex items-center justify-center">
                <span className="text-2xl font-bold text-[#050712]">
                  {user.first_name?.[0] || user.username?.[0] || '?'}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="font-bold text-[#f1f5f9] truncate">
                  {user.first_name || user.username || 'Anonymous'}
                </h2>
                {user.username && (
                  <p className="text-sm text-[#64748b]">@{user.username}</p>
                )}
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-[#1e293b]/50">
              <div className="flex justify-between items-center text-sm">
                <span className="text-[#64748b]">{t('telegramId')}</span>
                <span className="text-[#f1f5f9] font-mono">{user.telegram_id}</span>
              </div>
              <div className="flex justify-between items-center text-sm mt-2">
                <span className="text-[#64748b]">{t('refCode')}</span>
                <span className="text-[#00f5d4] font-mono">{user.ref_code}</span>
              </div>
            </div>
          </div>
        )}

        {/* Language Selection */}
        <div>
          <h3 className="text-sm font-medium text-[#64748b] uppercase tracking-wide mb-3">
            {t('language')}
          </h3>
          <div className="space-y-2">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                className={`w-full p-4 rounded-xl flex items-center justify-between transition-all ${
                  locale === lang.code
                    ? 'bg-[#00f5d4]/20 border border-[#00f5d4]/50'
                    : 'bg-[#1e293b]/40 border border-[#1e293b]/50 hover:bg-[#1e293b]/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{lang.code.toUpperCase()}</span>
                  <div className="text-left">
                    <p className="text-sm text-[#f1f5f9]">{lang.nativeName}</p>
                  </div>
                </div>
                {locale === lang.code && (
                  <span className="text-[#00f5d4]">OK</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* App Info */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 border border-[#1e293b]/50">
          <h3 className="text-sm font-medium text-[#64748b] uppercase tracking-wide mb-3">
            {t('about')}
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[#64748b]">{t('version')}</span>
              <span className="text-[#f1f5f9]">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#64748b]">{t('build')}</span>
              <span className="text-[#f1f5f9]">2024.12</span>
            </div>
          </div>
        </div>

        {/* Support Links */}
        <div className="space-y-2">
          <a
            href="https://t.me/pixelpets_support"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between p-4 rounded-xl bg-[#1e293b]/40 border border-[#1e293b]/50 hover:bg-[#1e293b]/60 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">HELP</span>
              <span className="text-sm text-[#f1f5f9]">{t('support')}</span>
            </div>
            <span className="text-[#64748b]">-&gt;</span>
          </a>
          <a
            href="https://t.me/pixelpets_channel"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between p-4 rounded-xl bg-[#1e293b]/40 border border-[#1e293b]/50 hover:bg-[#1e293b]/60 transition-colors"
          >
            <div className="flex items-center gap-3">
              <span className="text-xl">NEWS</span>
              <span className="text-sm text-[#f1f5f9]">{t('newsChannel')}</span>
            </div>
            <span className="text-[#64748b]">-&gt;</span>
          </a>
        </div>
      </div>
    </PageLayout>
  );
}
