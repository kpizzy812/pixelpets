'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { PageLayout } from '@/components/layout/page-layout';
import { RefStatsCard } from './ref-stats-card';
import { RefLevelCard } from './ref-level-card';
import { InviteCard } from './invite-card';
import { RefCardSkeleton, StatsCardSkeleton, LevelCardSkeleton } from '@/components/ui/skeleton';
import { ErrorState } from '@/components/ui/error-state';
import { useGameStore } from '@/store/game-store';
import { useTelegram } from '@/components/providers/telegram-provider';
import { showSuccess, showError } from '@/lib/toast';

export function ReferralsScreen() {
  const { referrals, referralsLoading, fetchReferrals } = useGameStore();
  const { webApp, isTelegram } = useTelegram();
  const [copied, setCopied] = useState(false);
  const t = useTranslations('referrals');

  useEffect(() => {
    fetchReferrals();
  }, [fetchReferrals]);

  const handleCopy = async () => {
    if (!referrals) return;
    try {
      await navigator.clipboard.writeText(referrals.ref_link);
      setCopied(true);
      showSuccess(t('linkCopied'));
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showError(t('failedToCopy'));
    }
  };

  const handleShare = () => {
    if (!referrals) return;

    // Use Telegram native share if available
    if (isTelegram && webApp) {
      const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(referrals.ref_link)}&text=${encodeURIComponent(referrals.share_text)}`;
      webApp.openTelegramLink(shareUrl);
    } else if (navigator.share) {
      navigator.share({
        text: referrals.share_text,
        url: referrals.ref_link
      });
    } else {
      handleCopy();
    }
  };

  // Calculate total referrals from all levels
  const totalReferrals = referrals?.levels.reduce((sum, lvl) => sum + lvl.referrals_count, 0) ?? 0;

  return (
    <PageLayout title={t('title')}>
      <div className="p-4 space-y-4">
        {referralsLoading && !referrals ? (
          <div className="space-y-4">
            <RefCardSkeleton />
            <StatsCardSkeleton />
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <LevelCardSkeleton key={i} />
              ))}
            </div>
          </div>
        ) : referrals ? (
          <>
            {/* Invite Card */}
            <InviteCard
              refLink={referrals.ref_link}
              refCode={referrals.ref_code}
              onCopy={handleCopy}
              onShare={handleShare}
              copied={copied}
            />

            {/* Stats Card */}
            <RefStatsCard
              totalReferrals={totalReferrals}
              activeReferrals={referrals.active_referrals_count}
              totalEarned={referrals.total_earned_xpet}
            />

            {/* Referral Levels */}
            <div className="space-y-3">
              <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wide">
                {t('levels')}
              </h2>
              {referrals.levels.map((level) => (
                <RefLevelCard
                  key={level.level}
                  level={level.level}
                  percentage={level.percent}
                  count={level.referrals_count}
                  earned={level.earned_xpet}
                  unlocked={level.unlocked}
                  unlockRequirement={level.unlock_requirement}
                  progress={level.progress}
                />
              ))}
            </div>
          </>
        ) : (
          <ErrorState
            icon="referrals"
            title={t('unableToLoad')}
            message={t('tryAgain')}
            onRetry={fetchReferrals}
          />
        )}
      </div>
    </PageLayout>
  );
}
