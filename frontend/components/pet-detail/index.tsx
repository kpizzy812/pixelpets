'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { PetImage } from '@/components/ui/pet-image';
import { Icon } from '@/components/ui/icon';
import { ProgressBar } from '@/components/ui/progress-bar';
import { useCountdown } from '@/hooks/use-countdown';
import { useHaptic } from '@/hooks/use-haptic';
import { useTelegram } from '@/components/providers/telegram-provider';
import { formatNumber } from '@/lib/format';
import type { Pet } from '@/types/pet';

interface PetDetailScreenProps {
  pet: Pet;
  onBack: () => void;
}

export function PetDetailScreen({ pet, onBack }: PetDetailScreenProps) {
  const t = useTranslations('petDetail');
  const tLevels = useTranslations('petLevels');
  const { tap } = useHaptic();
  const countdown = useCountdown(pet.trainingEndsAt);
  const { webApp, isTelegram } = useTelegram();

  // Setup Telegram back button
  useEffect(() => {
    if (!isTelegram || !webApp) return;

    const backButton = webApp.BackButton;
    backButton.show();

    const handleBack = () => {
      tap();
      onBack();
    };

    backButton.onClick(handleBack);

    return () => {
      backButton.offClick(handleBack);
      backButton.hide();
    };
  }, [isTelegram, webApp, onBack, tap]);

  const isTraining = pet.status === 'TRAINING';
  const isReady = pet.status === 'READY_TO_CLAIM' || (isTraining && countdown.isComplete);

  const getGradient = () => {
    switch (pet.rarity) {
      case 'Uncommon': return 'from-[#c7f464]/20 to-[#0d1220]';
      case 'Rare': return 'from-[#00f5d4]/20 to-[#0d1220]';
      case 'Epic': return 'from-[#a855f7]/20 to-[#0d1220]';
      case 'Legendary': return 'from-[#fbbf24]/20 to-[#0d1220]';
      case 'Mythic': return 'from-[#ff6b9d]/20 to-[#0d1220]';
      default: return 'from-[#1e293b]/50 to-[#0d1220]';
    }
  };

  const getRarityColor = () => {
    switch (pet.rarity) {
      case 'Uncommon': return '#c7f464';
      case 'Rare': return '#00f5d4';
      case 'Epic': return '#a855f7';
      case 'Legendary': return '#fbbf24';
      case 'Mythic': return '#ff6b9d';
      default: return '#94a3b8';
    }
  };

  const getLevelNumber = (): number => {
    if (pet.level === 'BABY') return 1;
    if (pet.level === 'ADULT') return 2;
    return 3;
  };

  const dailyProfit = pet.invested * pet.dailyRate / 100;

  return (
    <div className="flex flex-col h-full overflow-hidden tg-safe-top tg-safe-bottom">
      {/* Header with back button */}
      <div className="mx-4 mt-4 p-4 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <button
            onClick={() => { tap(); onBack(); }}
            className="flex items-center gap-2 text-[#94a3b8] hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="text-sm">{t('back')}</span>
          </button>
          <h1 className="text-xl font-bold text-[#f1f5f9]">{t('title')}</h1>
          <div className="w-16" /> {/* Spacer for centering */}
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto scrollbar-hide p-4 space-y-4">
        {/* Pet Card */}
        <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
          <div className="flex flex-col items-center">
            {/* Pet Image */}
            <div className={`w-48 h-48 rounded-3xl bg-gradient-to-br ${getGradient()} border border-[#334155]/30 overflow-hidden shadow-lg`}>
              <PetImage imageKey={pet.imageKey} level={pet.level} alt={pet.name} size={192} className="w-full h-full object-cover" />
            </div>

            {/* Pet Name & Level */}
            <h2 className="mt-4 text-2xl font-bold text-white">{pet.name}</h2>
            <div className="flex items-center gap-2 mt-1">
              <span
                className="text-sm font-medium px-2 py-0.5 rounded-full"
                style={{ backgroundColor: `${getRarityColor()}20`, color: getRarityColor() }}
              >
                {pet.rarity}
              </span>
              <span className="text-sm text-[#94a3b8]">•</span>
              <span className="text-sm text-[#94a3b8]">{tLevels(pet.level)} ({getLevelNumber()})</span>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label={t('invested')}
            value={formatNumber(pet.invested)}
            suffix={<XpetCoin size={14} />}
            color="#00f5d4"
          />
          <StatCard
            label={t('dailyRate')}
            value={`+${pet.dailyRate}%`}
            color="#c7f464"
          />
          <StatCard
            label={t('dailyProfit')}
            value={`+${formatNumber(dailyProfit)}`}
            suffix={<XpetCoin size={14} />}
            color="#fbbf24"
          />
          <StatCard
            label={t('totalEarned')}
            value={formatNumber(pet.profitClaimed)}
            suffix={<XpetCoin size={14} />}
            color="#22d3ee"
          />
        </div>

        {/* ROI Progress */}
        <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-[#94a3b8]">{t('roiProgress')}</span>
            <span className="text-sm font-medium text-[#c7f464]">{pet.roiProgress.toFixed(1)}%</span>
          </div>
          <ProgressBar progress={pet.roiProgress / 100} />
          <div className="flex items-center justify-between mt-2 text-xs text-[#64748b]">
            <span>{formatNumber(pet.profitClaimed)} / {formatNumber(pet.roiCap)}</span>
            <span>{t('roiCap')}: {formatNumber(pet.roiCap)} <XpetCoin size={10} className="inline" /></span>
          </div>
        </div>

        {/* Training Progress */}
        {isTraining && !countdown.isComplete && (
          <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-[#94a3b8]">{t('trainingProgress')}</span>
              <span className="text-sm font-mono text-[#c7f464]">{countdown.formatted}</span>
            </div>
            <ProgressBar progress={countdown.progress} />
          </div>
        )}

        {/* Upgrade Info */}
        {pet.upgradeCost && pet.level !== 'MYTHIC' && (
          <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-[#c7f464]/10 flex items-center justify-center">
                  <Icon name="levelup" size={32} />
                </div>
                <div>
                  <span className="text-sm text-[#94a3b8]">{t('nextLevel')}</span>
                  <p className="text-white font-medium">{tLevels(pet.level === 'BABY' ? 'ADULT' : 'MYTHIC')}</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs text-[#64748b]">{t('upgradeCost')}</span>
                <p className="text-[#c7f464] font-bold flex items-center gap-1">
                  {formatNumber(pet.upgradeCost)} <XpetCoin size={14} />
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Mint NFT Section - Blurred with SOON */}
        <div className="relative">
          <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 blur-[2px] pointer-events-none">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-[#a855f7]/20 to-[#ec4899]/20 flex items-center justify-center">
                <svg className="w-8 h-8 text-[#a855f7]" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white">{t('mintNft')}</h3>
                <p className="text-sm text-[#94a3b8]">{t('mintNftDescription')}</p>
              </div>
              <button className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#a855f7] to-[#ec4899] text-white font-medium">
                {t('mint')}
              </button>
            </div>
          </div>
          {/* MINT NFT SOON Badge Overlay */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="px-6 py-2 rounded-full bg-[#1e293b]/90 border border-[#334155] flex items-center gap-2">
              <svg className="w-5 h-5 text-[#a855f7]" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
              <span className="text-lg font-bold text-[#c7f464]">MINT NFT SOON</span>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
          <h3 className="text-sm font-medium text-[#64748b] uppercase tracking-wide mb-3">
            {t('additionalInfo')}
          </h3>
          <div className="space-y-2">
            <InfoRow label={t('petId')} value={`#${pet.id}`} />
            <InfoRow label={t('slotIndex')} value={`${pet.slotIndex + 1}`} />
          </div>
        </div>
      </div>
    </div>
  );
}

interface StatCardProps {
  label: string;
  value: string;
  suffix?: React.ReactNode;
  color: string;
}

function StatCard({ label, value, suffix, color }: StatCardProps) {
  return (
    <div className="p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50">
      <span className="text-xs text-[#64748b]">{label}</span>
      <div className="mt-1 flex items-center gap-1 text-lg font-bold" style={{ color }}>
        {value}
        {suffix}
      </div>
    </div>
  );
}

interface InfoRowProps {
  label: string;
  value: string;
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-[#64748b]">{label}</span>
      <span className="text-sm text-white font-medium">{value}</span>
    </div>
  );
}
