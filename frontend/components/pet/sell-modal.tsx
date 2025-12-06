'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { PetImage } from '@/components/ui/pet-image';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore } from '@/store/game-store';
import { showSuccess, showError } from '@/lib/toast';
import { formatNumber } from '@/lib/format';
import { useTelegram } from '@/components/providers/telegram-provider';
import type { Pet } from '@/types/pet';

interface SellModalProps {
  isOpen: boolean;
  onClose: () => void;
  pet: Pet | null;
}

const SELL_RATE = 0.85; // 85% refund

export function SellModal({ isOpen, onClose, pet }: SellModalProps) {
  const { sellPet } = useGameStore();
  const [isProcessing, setIsProcessing] = useState(false);
  const t = useTranslations('sellModal');
  const tCommon = useTranslations('common');
  const { webApp } = useTelegram();

  // Handle Telegram Back Button
  useEffect(() => {
    if (!isOpen || !webApp?.BackButton) return;

    const handleBackClick = () => {
      if (!isProcessing) {
        onClose();
      }
    };

    webApp.BackButton.onClick(handleBackClick);
    webApp.BackButton.show();

    return () => {
      webApp.BackButton.offClick(handleBackClick);
      webApp.BackButton.hide();
    };
  }, [isOpen, webApp, isProcessing, onClose]);

  if (!isOpen || !pet) return null;

  const refundAmount = pet.invested * SELL_RATE;
  const lossAmount = pet.invested - refundAmount;

  const handleSell = async () => {
    setIsProcessing(true);

    try {
      const refund = await sellPet(Number(pet.id));
      showSuccess(t('soldMessage', { name: pet.name, refund: formatNumber(refund) }));
      onClose();
    } catch (err) {
      showError(err instanceof Error ? err.message : t('failedToSell'));
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isProcessing ? undefined : onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-red-400">{t('title')}</h2>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            X
          </button>
        </div>

        {/* Warning */}
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 mb-6 text-center">
          <span className="text-3xl mb-2 block">!!!</span>
          <p className="text-sm text-red-400 font-medium">{t('warning')}</p>
        </div>

        {/* Pet Info */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 mb-6 text-center">
          <div className="flex justify-center mb-3">
            <PetImage imageKey={pet.imageKey} level={pet.level} alt={pet.name} size={80} className="rounded-2xl" />
          </div>
          <h3 className="text-lg font-bold text-[#f1f5f9]">{pet.name}</h3>
          <p className="text-sm text-[#64748b] mt-1">{pet.level}</p>
        </div>

        {/* Sell Info */}
        <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-6 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">{t('totalInvested')}</span>
            <span className="text-sm text-[#f1f5f9] inline-flex items-center gap-1">{formatNumber(pet.invested)} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">{t('sellRate')}</span>
            <span className="text-sm text-[#fbbf24]">{formatNumber(SELL_RATE * 100, 0)}%</span>
          </div>
          <div className="h-px bg-[#334155]" />
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">{t('youReceive')}</span>
            <span className="text-sm text-[#c7f464] font-medium inline-flex items-center gap-1">{formatNumber(refundAmount)} <XpetCoin size={18} /></span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">{t('loss')}</span>
            <span className="text-sm text-red-400 inline-flex items-center gap-1">-{formatNumber(lossAmount)} <XpetCoin size={18} /></span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="flex-1 py-4 rounded-xl font-medium bg-[#1e293b]/60 text-[#94a3b8] hover:bg-[#1e293b] transition-all disabled:opacity-50"
          >
            {tCommon('cancel')}
          </button>
          <button
            onClick={handleSell}
            disabled={isProcessing}
            className="flex-1 py-4 rounded-xl font-medium bg-red-500 text-white hover:bg-red-600 transition-all disabled:opacity-50"
          >
            {isProcessing ? t('selling') : t('sellPet')}
          </button>
        </div>
      </div>
    </div>
  );
}
