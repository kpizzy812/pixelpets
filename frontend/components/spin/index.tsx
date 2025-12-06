'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import { PageLayout } from '@/components/layout/page-layout';
import { Wheel } from './wheel';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { spinApi } from '@/lib/api';
import { showReward, showError } from '@/lib/toast';
import { formatNumber } from '@/lib/format';
import { useHaptic } from '@/hooks/use-haptic';
import type { SpinReward, SpinWheelResponse } from '@/types/api';

export function SpinScreen() {
  const balance = useBalance();
  const { updateBalance } = useGameStore();
  const t = useTranslations('spin');
  const haptic = useHaptic();
  const hapticIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const [wheelData, setWheelData] = useState<SpinWheelResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSpinning, setIsSpinning] = useState(false);
  const [winningIndex, setWinningIndex] = useState<number | null>(null);
  const [lastWin, setLastWin] = useState<{ reward: SpinReward; amount: number } | null>(null);
  const [countdown, setCountdown] = useState<string | null>(null);

  const fetchWheel = useCallback(async () => {
    try {
      const data = await spinApi.wheel();
      setWheelData(data);
    } catch (err) {
      console.error('Failed to fetch wheel:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWheel();
  }, [fetchWheel]);

  // Countdown timer for free spin
  useEffect(() => {
    if (!wheelData?.next_free_spin_at) {
      setCountdown(null);
      return;
    }

    const updateCountdown = () => {
      const next = new Date(wheelData.next_free_spin_at! + 'Z').getTime();
      const now = Date.now();
      const diff = next - now;

      if (diff <= 0) {
        setCountdown(null);
        fetchWheel(); // Refresh to enable free spin
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setCountdown(
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      );
    };

    updateCountdown();
    const interval = setInterval(updateCountdown, 1000);
    return () => clearInterval(interval);
  }, [wheelData?.next_free_spin_at, fetchWheel]);

  const handleSpin = async (isFree: boolean) => {
    if (isSpinning || !wheelData) return;

    // Check balance for paid spin
    if (!isFree && balance < wheelData.paid_spin_cost) {
      showError(t('insufficientBalance'));
      return;
    }

    // Haptic on button press
    haptic.press();

    setIsSpinning(true);
    setLastWin(null);

    // Start periodic haptic during spin (simulates pointer hitting segments)
    // Fast at first (50ms), slowing down as wheel decelerates
    let interval = 50;
    let elapsed = 0;
    const totalDuration = 4000;

    const tickHaptic = () => {
      if (elapsed >= totalDuration) {
        if (hapticIntervalRef.current) {
          clearTimeout(hapticIntervalRef.current);
          hapticIntervalRef.current = null;
        }
        return;
      }

      haptic.impact('light');
      elapsed += interval;

      // Slow down the haptic as wheel decelerates
      // First 1s: 50ms, 1-2s: 80ms, 2-3s: 150ms, 3-4s: 300ms
      if (elapsed > 3000) {
        interval = 300;
      } else if (elapsed > 2000) {
        interval = 150;
      } else if (elapsed > 1000) {
        interval = 80;
      }

      hapticIntervalRef.current = setTimeout(tickHaptic, interval);
    };

    hapticIntervalRef.current = setTimeout(tickHaptic, interval);

    try {
      const result = await spinApi.spin(isFree);
      setWinningIndex(result.winning_index);
      updateBalance(result.new_balance);

      // Show result after animation
      setTimeout(() => {
        // Strong haptic when reward appears
        haptic.notification('success');
        setLastWin({ reward: result.reward, amount: result.amount_won });
        if (result.amount_won > 0) {
          showReward(result.amount_won);
        }
      }, 4000);
    } catch (err) {
      // Stop haptic interval on error
      if (hapticIntervalRef.current) {
        clearTimeout(hapticIntervalRef.current);
        hapticIntervalRef.current = null;
      }
      setIsSpinning(false);
      showError(err instanceof Error ? err.message : t('spinFailed'));
    }
  };

  const handleSpinEnd = () => {
    setIsSpinning(false);
    setWinningIndex(null);
    fetchWheel(); // Refresh status
  };

  if (isLoading) {
    return (
      <PageLayout title={t('title')}>
        <div className="flex items-center justify-center h-[60vh]">
          <div className="w-72 h-72 rounded-full bg-[#1a2235] animate-pulse" />
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout title={t('title')}>
      <div className="flex flex-col items-center px-4 py-6 space-y-6">
        {/* Balance Display */}
        <div className="w-full p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex justify-between items-center">
          <span className="text-sm text-[#94a3b8]">{t('yourBalance')}</span>
          <span className="text-sm font-medium text-[#c7f464] inline-flex items-center gap-1">
            {formatNumber(balance)} <XpetCoin size={18} />
          </span>
        </div>

        {/* Today's Stats */}
        <div className="w-full flex gap-3">
          <div className="flex-1 p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 text-center">
            <div className="text-xs text-[#64748b]">{t('spinsToday')}</div>
            <div className="text-lg font-bold text-white">{wheelData?.spins_today || 0}</div>
          </div>
          <div className="flex-1 p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 text-center">
            <div className="text-xs text-[#64748b]">{t('wonToday')}</div>
            <div className="text-lg font-bold text-[#c7f464] inline-flex items-center justify-center gap-1">
              {formatNumber(wheelData?.winnings_today || 0)} <XpetCoin size={16} />
            </div>
          </div>
        </div>

        {/* Wheel */}
        <div className="relative">
          <Wheel
            rewards={wheelData?.rewards || []}
            isSpinning={isSpinning}
            winningIndex={winningIndex}
            onSpinEnd={handleSpinEnd}
          />

          {/* Last Win Overlay */}
          {lastWin && !isSpinning && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/60 rounded-full animate-fade-in">
              <div className="text-center">
                <div className="mb-2 flex justify-center">
                  <Image
                    src="/XPET.png"
                    alt="XPET"
                    width={48}
                    height={48}
                    className="drop-shadow-lg"
                  />
                </div>
                {lastWin.amount > 0 ? (
                  <>
                    <div className="text-lg font-bold text-[#c7f464]">
                      +{formatNumber(lastWin.amount)}
                    </div>
                    <div className="text-xs text-[#94a3b8]">XPET</div>
                  </>
                ) : (
                  <div className="text-sm text-[#94a3b8]">{t('tryAgain')}</div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Spin Buttons - Horizontal Layout */}
        <div className="w-full flex gap-3">
          {/* Free Spin Button */}
          <button
            onClick={() => handleSpin(true)}
            disabled={isSpinning || !wheelData?.can_free_spin}
            className={`flex-1 py-3 px-4 rounded-xl font-bold transition-all ${
              wheelData?.can_free_spin && !isSpinning
                ? 'bg-gradient-to-r from-[#c7f464] to-[#a3d944] text-[#0d1220] hover:opacity-90 active:scale-[0.98]'
                : 'bg-[#1a2235] text-[#64748b] cursor-not-allowed'
            }`}
          >
            {isSpinning ? (
              <span className="inline-flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
              </span>
            ) : wheelData?.can_free_spin ? (
              <span className="text-sm">{t('freeSpin')}</span>
            ) : (
              <span className="text-xs">{countdown || '...'}</span>
            )}
          </button>

          {/* Paid Spin Button */}
          <button
            onClick={() => handleSpin(false)}
            disabled={isSpinning || balance < (wheelData?.paid_spin_cost || 1)}
            className={`flex-1 py-3 px-4 rounded-xl font-bold transition-all ${
              !isSpinning && balance >= (wheelData?.paid_spin_cost || 1)
                ? 'bg-gradient-to-r from-[#FFD700] to-[#FFA500] text-[#0d1220] hover:opacity-90 active:scale-[0.98]'
                : 'bg-[#1a2235] text-[#64748b] cursor-not-allowed'
            }`}
          >
            <span className="inline-flex items-center justify-center gap-1.5 text-sm">
              {wheelData?.paid_spin_cost || 1} <XpetCoin size={16} />
            </span>
          </button>
        </div>

        {/* Info */}
        <p className="text-xs text-[#64748b] text-center">
          {t('spinInfo')}
        </p>
      </div>
    </PageLayout>
  );
}
