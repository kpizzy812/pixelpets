'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { PageLayout } from '@/components/layout/page-layout';
import { FloatingSpinButton } from '@/components/layout/floating-spin-button';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { Icon, type IconName } from '@/components/ui/icon';
import { useTelegram } from '@/components/providers/telegram-provider';
import { authApi } from '@/lib/api';
import { formatNumber } from '@/lib/format';
import { useHaptic } from '@/hooks/use-haptic';
import { useBackButton } from '@/hooks/use-back-button';
import type { ProfileResponse } from '@/types/api';

export function ProfileScreen() {
  const t = useTranslations('profile');
  const tCommon = useTranslations('common');
  const router = useRouter();
  const { user: telegramUser } = useTelegram();
  const { tap } = useHaptic();

  useBackButton({
    show: true,
    onBack: () => {
      router.push('/');
      return true;
    },
  });

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await authApi.profile();
        setProfile(data);
      } catch (err) {
        console.error('Failed to fetch profile:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const getAvatarUrl = () => {
    if (!telegramUser) return null;
    return telegramUser.photo_url || null;
  };

  const getUserName = () => {
    if (!profile) return '';
    if (profile.first_name && profile.last_name) {
      return `${profile.first_name} ${profile.last_name}`;
    }
    return profile.first_name || profile.username || 'User';
  };

  const getUserInitials = () => {
    if (!profile) return 'U';
    const firstInitial = profile.first_name?.[0] || '';
    const lastInitial = profile.last_name?.[0] || '';
    return (firstInitial + lastInitial).toUpperCase() || 'U';
  };

  const avatarUrl = getAvatarUrl();

  const handleNavigate = (path: string) => {
    tap();
    router.push(path);
  };

  if (isLoading) {
    return (
      <PageLayout title={t('title')}>
        <div className="p-4 space-y-4">
          {/* Avatar skeleton */}
          <div className="flex flex-col items-center py-6">
            <div className="w-24 h-24 rounded-full bg-[#1a2235] animate-pulse" />
            <div className="mt-3 h-6 w-32 bg-[#1a2235] animate-pulse rounded" />
            <div className="mt-1 h-4 w-24 bg-[#1a2235] animate-pulse rounded" />
          </div>
          {/* Stats skeleton */}
          <div className="grid grid-cols-2 gap-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-[#1a2235] animate-pulse rounded-xl" />
            ))}
          </div>
        </div>
      </PageLayout>
    );
  }

  if (!profile) {
    return (
      <PageLayout title={t('title')}>
        <div className="flex items-center justify-center h-[60vh]">
          <p className="text-[#64748b]">{tCommon('error')}</p>
        </div>
      </PageLayout>
    );
  }

  const stats = profile.stats;

  return (
    <PageLayout title={t('title')}>
      <div className="p-4 space-y-4">
        {/* Profile Header */}
        <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
          <div className="flex flex-col items-center">
            {/* Avatar */}
            {avatarUrl ? (
              <img
                src={avatarUrl}
                alt="Avatar"
                className="w-24 h-24 rounded-full border-3 border-[#00f5d4]/40 shadow-lg shadow-[#00f5d4]/10"
              />
            ) : (
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#00f5d4] to-[#c7f464] flex items-center justify-center text-[#050712] font-bold text-3xl shadow-lg shadow-[#00f5d4]/20">
                {getUserInitials()}
              </div>
            )}

            {/* Name */}
            <h2 className="mt-3 text-xl font-bold text-white">
              {getUserName()}
            </h2>

            {/* Username & ID */}
            <div className="mt-1 flex items-center gap-2 text-sm text-[#64748b]">
              {profile.username && (
                <span>@{profile.username}</span>
              )}
              <span className="text-[#334155]">|</span>
              <span>ID: {profile.telegram_id}</span>
            </div>

            {/* Balance */}
            <div className="mt-4 px-5 py-2 rounded-full bg-[#1e293b]/60 border border-[#334155]/40">
              <span className="text-lg font-bold text-[#c7f464] inline-flex items-center gap-1.5">
                {formatNumber(profile.balance_xpet)} <XpetCoin size={20} />
              </span>
            </div>
          </div>
        </div>

        {/* Pets Stats */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium text-[#64748b] uppercase tracking-wide px-1">
            {t('petsSection')}
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon="paw"
              iconColor="#00f5d4"
              label={t('petsOwned')}
              value={stats.total_pets_owned.toString()}
            />
            <StatCard
              icon="coin"
              iconColor="#c7f464"
              label={t('petsValue')}
              value={formatNumber(stats.total_pets_value)}
              suffix={<XpetCoin size={14} />}
            />
            <StatCard
              icon="trophy"
              iconColor="#fbbf24"
              label={t('petsEvolved')}
              value={stats.total_pets_evolved.toString()}
            />
            <StatCard
              icon="chart"
              iconColor="#22d3ee"
              label={t('totalEarned')}
              value={formatNumber(stats.total_claimed)}
              suffix={<XpetCoin size={14} />}
            />
          </div>
        </div>

        {/* Spin Stats */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium text-[#64748b] uppercase tracking-wide px-1">
            {t('spinSection')}
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon="spin"
              iconColor="#f472b6"
              label={t('totalSpins')}
              value={stats.total_spins.toString()}
            />
            <StatCard
              icon="gift"
              iconColor="#a78bfa"
              label={t('spinWinnings')}
              value={formatNumber(stats.total_spin_wins)}
              suffix={<XpetCoin size={14} />}
            />
          </div>
        </div>

        {/* Referral Stats */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium text-[#64748b] uppercase tracking-wide px-1">
            {t('referralsSection')}
          </h3>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              icon="users"
              iconColor="#38bdf8"
              label={t('totalReferrals')}
              value={stats.total_referrals.toString()}
            />
            <StatCard
              icon="user-check"
              iconColor="#4ade80"
              label={t('activeReferrals')}
              value={stats.active_referrals.toString()}
            />
            <div className="col-span-2">
              <StatCard
                icon="dollar"
                iconColor="#c7f464"
                label={t('refEarnings')}
                value={formatNumber(stats.total_ref_earned)}
                suffix={<XpetCoin size={14} />}
                large
              />
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="space-y-2">
          <h3 className="text-xs font-medium text-[#64748b] uppercase tracking-wide px-1">
            {t('quickLinks')}
          </h3>
          <div className="grid grid-cols-3 gap-3">
            <QuickLinkButton
              icon="trophy"
              label={t('hallOfFame')}
              color="#fbbf24"
              onClick={() => handleNavigate('/hall-of-fame')}
            />
            <QuickLinkButton
              icon="history"
              label={t('transactions')}
              color="#94a3b8"
              onClick={() => handleNavigate('/transactions')}
            />
            <QuickLinkButton
              icon="settings"
              label={t('settings')}
              color="#64748b"
              onClick={() => handleNavigate('/settings')}
            />
          </div>
        </div>

        {/* Member Since */}
        <div className="text-center text-xs text-[#475569] py-2">
          {t('memberSince')}: {new Date(profile.created_at).toLocaleDateString()}
        </div>
      </div>

      <FloatingSpinButton />
    </PageLayout>
  );
}

interface StatCardProps {
  icon: IconName;
  iconColor: string;
  label: string;
  value: string;
  suffix?: React.ReactNode;
  large?: boolean;
}

function StatCard({ icon, iconColor, label, value, suffix, large }: StatCardProps) {
  return (
    <div className={`p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 ${large ? 'flex items-center justify-between' : ''}`}>
      <div className={`flex items-center gap-2 ${large ? '' : 'mb-2'}`}>
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${iconColor}15` }}
        >
          <Icon name={icon} size={18} style={{ color: iconColor }} />
        </div>
        <span className="text-xs text-[#94a3b8]">{label}</span>
      </div>
      <div className={`flex items-center gap-1 ${large ? 'text-lg' : 'text-base'} font-bold text-white`}>
        {value}
        {suffix}
      </div>
    </div>
  );
}

interface QuickLinkButtonProps {
  icon: IconName;
  label: string;
  color: string;
  onClick: () => void;
}

function QuickLinkButton({ icon, label, color, onClick }: QuickLinkButtonProps) {
  return (
    <button
      onClick={onClick}
      className="p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex flex-col items-center gap-2 hover:bg-[#1e293b]/50 transition-all active:scale-95"
    >
      <Icon name={icon} size={24} style={{ color }} />
      <span className="text-xs text-[#94a3b8]">{label}</span>
    </button>
  );
}
