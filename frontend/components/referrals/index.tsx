'use client';

import { useState, useEffect } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { RefStatsCard } from './ref-stats-card';
import { RefLevelCard } from './ref-level-card';
import { InviteCard } from './invite-card';
import { RefCardSkeleton, StatsCardSkeleton, LevelCardSkeleton } from '@/components/ui/skeleton';
import { ErrorState } from '@/components/ui/error-state';
import { useGameStore } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';

export function ReferralsScreen() {
  const { referrals, referralsLoading, fetchReferrals } = useGameStore();
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchReferrals();
  }, [fetchReferrals]);

  const handleCopy = async () => {
    if (!referrals) return;
    try {
      await navigator.clipboard.writeText(referrals.ref_link);
      setCopied(true);
      showSuccess('Link copied!');
      setTimeout(() => setCopied(false), 2000);
    } catch {
      showError('Failed to copy link');
    }
  };

  const handleShare = () => {
    if (!referrals) return;
    const text = `Join Pixel Pets and earn XPET! ${referrals.ref_link}`;

    if (navigator.share) {
      navigator.share({ text, url: referrals.ref_link });
    } else {
      handleCopy();
    }
  };

  return (
    <PageLayout title="Referrals">
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
              totalReferrals={referrals.total_referrals}
              activeReferrals={referrals.active_referrals}
              totalEarned={referrals.total_earned}
            />

            {/* Referral Levels */}
            <div className="space-y-3">
              <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wide">
                Referral Levels
              </h2>
              {referrals.levels.map((level) => (
                <RefLevelCard
                  key={level.level}
                  level={level.level}
                  percentage={level.percentage}
                  count={level.count}
                  earned={level.earned}
                  unlocked={level.unlocked}
                />
              ))}
            </div>
          </>
        ) : (
          <ErrorState
            icon="referrals"
            title="Unable to Load Referrals"
            message="Something went wrong. Please try again."
            onRetry={fetchReferrals}
          />
        )}
      </div>
    </PageLayout>
  );
}
