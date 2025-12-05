'use client';

import { useState } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { useGameStore } from '@/store/game-store';
import { useBackButton } from '@/hooks/use-back-button';
import { useHaptic } from '@/hooks/use-haptic';

type Language = 'en' | 'ru' | 'de' | 'es' | 'fr' | 'pt' | 'it';

interface LanguageOption {
  code: Language;
  name: string;
  nativeName: string;
}

const LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'fr', name: 'French', nativeName: 'Français' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano' },
];

export function SettingsScreen() {
  const { user } = useGameStore();
  const [selectedLanguage, setSelectedLanguage] = useState<Language>(
    (user?.language_code as Language) || 'en'
  );
  const [isSaving, setIsSaving] = useState(false);
  const { selection, success } = useHaptic();

  // Enable Telegram back button for this page
  useBackButton();

  const handleLanguageChange = async (lang: Language) => {
    if (lang === selectedLanguage) return;
    selection();
    setIsSaving(true);
    setSelectedLanguage(lang);
    // TODO: Save language preference to backend
    await new Promise((resolve) => setTimeout(resolve, 500));
    success();
    setIsSaving(false);
  };

  return (
    <PageLayout title="Settings">
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
                <span className="text-[#64748b]">Telegram ID</span>
                <span className="text-[#f1f5f9] font-mono">{user.telegram_id}</span>
              </div>
              <div className="flex justify-between items-center text-sm mt-2">
                <span className="text-[#64748b]">Ref Code</span>
                <span className="text-[#00f5d4] font-mono">{user.ref_code}</span>
              </div>
            </div>
          </div>
        )}

        {/* Language Selection */}
        <div>
          <h3 className="text-sm font-medium text-[#64748b] uppercase tracking-wide mb-3">
            Language
          </h3>
          <div className="space-y-2">
            {LANGUAGES.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleLanguageChange(lang.code)}
                disabled={isSaving}
                className={`w-full p-4 rounded-xl flex items-center justify-between transition-all ${
                  selectedLanguage === lang.code
                    ? 'bg-[#00f5d4]/20 border border-[#00f5d4]/50'
                    : 'bg-[#1e293b]/40 border border-[#1e293b]/50 hover:bg-[#1e293b]/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-lg">{lang.code === 'en' ? 'EN' : lang.code.toUpperCase()}</span>
                  <div className="text-left">
                    <p className="text-sm text-[#f1f5f9]">{lang.nativeName}</p>
                    <p className="text-xs text-[#64748b]">{lang.name}</p>
                  </div>
                </div>
                {selectedLanguage === lang.code && (
                  <span className="text-[#00f5d4]">OK</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* App Info */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 border border-[#1e293b]/50">
          <h3 className="text-sm font-medium text-[#64748b] uppercase tracking-wide mb-3">
            About
          </h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-[#64748b]">Version</span>
              <span className="text-[#f1f5f9]">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#64748b]">Build</span>
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
              <span className="text-sm text-[#f1f5f9]">Support</span>
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
              <span className="text-sm text-[#f1f5f9]">News Channel</span>
            </div>
            <span className="text-[#64748b]">-&gt;</span>
          </a>
        </div>
      </div>
    </PageLayout>
  );
}
