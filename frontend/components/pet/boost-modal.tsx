'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { boostsApi } from '@/lib/api';
import { showSuccess, showError } from '@/lib/toast';
import { useHaptic } from '@/hooks/use-haptic';
import { formatNumber } from '@/lib/format';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import type { Pet } from '@/types/pet';
import type {
  SnackType,
  SnackPricesResponse,
  RoiBoostPricesResponse,
  AutoClaimStatusResponse,
} from '@/types/api';

interface BoostModalProps {
  isOpen: boolean;
  onClose: () => void;
  pet: Pet | null;
}

type BoostTab = 'snacks' | 'roi' | 'autoclaim';

const SNACK_IMAGES: Record<SnackType, string> = {
  cookie: '/pixelicons/coockie.png',
  steak: '/pixelicons/stake.png',
  cake: '/pixelicons/cake.png',
};

const SNACK_NAMES: Record<SnackType, string> = {
  cookie: 'Cookie',
  steak: 'Steak',
  cake: 'Cake',
};

const ROI_OPTIONS = ['5', '10', '15', '20', '25'];

export function BoostModal({ isOpen, onClose, pet }: BoostModalProps) {
  const router = useRouter();
  const balance = useBalance();
  const { updateBalance } = useGameStore();
  const [activeTab, setActiveTab] = useState<BoostTab>('snacks');
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const { impact, success, error: hapticError, tap } = useHaptic();
  const t = useTranslations('boosts');

  const handleInsufficientBalance = () => {
    tap();
    onClose();
    router.push('/wallet');
  };

  // Data states
  const [snackPrices, setSnackPrices] = useState<SnackPricesResponse | null>(null);
  const [roiPrices, setRoiPrices] = useState<RoiBoostPricesResponse | null>(null);
  const [autoClaimStatus, setAutoClaimStatus] = useState<AutoClaimStatusResponse | null>(null);

  // Selection states
  const [selectedSnack, setSelectedSnack] = useState<SnackType>('cookie');
  const [selectedRoiOption, setSelectedRoiOption] = useState<string>('5');
  const [selectedMonths, setSelectedMonths] = useState<number>(1);

  useEffect(() => {
    if (isOpen) {
      impact('light');
      loadData();
    }
  }, [isOpen, impact, pet?.id]);

  const loadData = async () => {
    if (!pet) return;
    setIsLoading(true);
    try {
      const [snacks, roi, autoClaim] = await Promise.all([
        boostsApi.snackPrices(Number(pet.id)),
        boostsApi.roiPrices(Number(pet.id)),
        boostsApi.autoClaimStatus(),
      ]);
      setSnackPrices(snacks);
      setRoiPrices(roi);
      setAutoClaimStatus(autoClaim);
    } catch (err) {
      console.error('Failed to load boost data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen || !pet) return null;

  const handleClose = () => {
    tap();
    onClose();
  };

  const handleBuySnack = async () => {
    if (!snackPrices) return;
    const price = snackPrices.prices[selectedSnack];
    if (!price || balance < Number(price.cost)) return;

    setIsProcessing(true);
    try {
      const result = await boostsApi.buySnack(Number(pet.id), selectedSnack);
      success();
      updateBalance(Number(result.new_balance));
      showSuccess(t('snackPurchased', { snack: SNACK_NAMES[selectedSnack], bonus: price.bonus_percent }));
      await loadData();
    } catch (err) {
      hapticError();
      showError(err instanceof Error ? err.message : t('purchaseFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBuyRoiBoost = async () => {
    if (!roiPrices) return;
    const option = roiPrices.options[`+${selectedRoiOption}%`];
    if (!option || !option.can_buy || balance < Number(option.cost)) return;

    setIsProcessing(true);
    try {
      const boostDecimal = Number(selectedRoiOption) / 100;
      const result = await boostsApi.buyRoiBoost(Number(pet.id), boostDecimal);
      success();
      updateBalance(Number(result.new_balance));
      showSuccess(t('roiBoostPurchased', { percent: selectedRoiOption }));
      await loadData();
    } catch (err) {
      hapticError();
      showError(err instanceof Error ? err.message : t('purchaseFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBuyAutoClaim = async () => {
    if (!autoClaimStatus || autoClaimStatus.is_active) return;
    const cost = getAutoClaimCost(selectedMonths);
    if (balance < cost) return;

    setIsProcessing(true);
    try {
      const result = await boostsApi.buyAutoClaim(selectedMonths);
      success();
      updateBalance(Number(result.new_balance));
      showSuccess(t('autoClaimActivated', { months: selectedMonths }));
      await loadData();
    } catch (err) {
      hapticError();
      showError(err instanceof Error ? err.message : t('purchaseFailed'));
    } finally {
      setIsProcessing(false);
    }
  };

  const getAutoClaimCost = (months: number): number => {
    const baseCost = 5;
    const discounts: Record<number, number> = { 1: 0, 3: 0.1, 6: 0.2, 12: 0.3 };
    const discount = discounts[months] || 0;
    return baseCost * months * (1 - discount);
  };

  const renderSnacksTab = () => {
    if (isLoading) {
      return <div className="text-center py-8 text-[#64748b]">{t('loading')}</div>;
    }

    if (!snackPrices) {
      return <div className="text-center py-8 text-[#64748b]">{t('loadError')}</div>;
    }

    if (snackPrices.active_snack) {
      return (
        <div className="p-4 rounded-xl bg-[#c7f464]/10 border border-[#c7f464]/30 text-center">
          <Image src={SNACK_IMAGES[snackPrices.active_snack as SnackType]} alt={snackPrices.active_snack} width={48} height={48} className="mx-auto mb-2" />
          <p className="text-sm text-[#c7f464]">
            {t('activeSnack', { snack: SNACK_NAMES[snackPrices.active_snack as SnackType] })}
          </p>
          <p className="text-xs text-[#94a3b8] mt-1">{t('waitForClaim')}</p>
        </div>
      );
    }

    const snackTypes: SnackType[] = ['cookie', 'steak', 'cake'];

    return (
      <div className="space-y-4">
        <p className="text-xs text-[#94a3b8] text-center">{t('snackDescription')}</p>

        {/* Snack Selection */}
        <div className="grid grid-cols-3 gap-2">
          {snackTypes.map((snackType) => {
            const price = snackPrices.prices[snackType];
            if (!price) return null;
            const isSelected = selectedSnack === snackType;
            return (
              <button
                key={snackType}
                onClick={() => { tap(); setSelectedSnack(snackType); }}
                className={`p-3 rounded-xl border transition-all ${
                  isSelected
                    ? 'bg-[#c7f464]/20 border-[#c7f464]/50'
                    : 'bg-[#1e293b]/40 border-[#334155]/30 hover:border-[#334155]/60'
                }`}
              >
                <Image src={SNACK_IMAGES[snackType]} alt={snackType} width={32} height={32} className="mx-auto mb-1" />
                <span className="text-xs font-medium text-[#f1f5f9]">{SNACK_NAMES[snackType]}</span>
                <span className="text-xs text-[#c7f464] block">+{price.bonus_percent}%</span>
              </button>
            );
          })}
        </div>

        {/* Selected Snack Info */}
        {snackPrices.prices[selectedSnack] && (
          <div className="p-4 rounded-xl bg-[#1e293b]/40 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('dailyProfit')}</span>
              <span className="text-[#f1f5f9]">${formatNumber(snackPrices.daily_profit)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('bonusAmount')}</span>
              <span className="text-[#c7f464]">+${formatNumber(snackPrices.prices[selectedSnack].bonus_amount)}</span>
            </div>
            <div className="h-px bg-[#334155]" />
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('cost')}</span>
              <span className="text-[#f1f5f9] inline-flex items-center gap-1">
                {formatNumber(snackPrices.prices[selectedSnack].cost)} <XpetCoin size={16} />
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('netBenefit')}</span>
              <span className="text-[#c7f464] inline-flex items-center gap-1">
                +{formatNumber(snackPrices.prices[selectedSnack].net_benefit)} <XpetCoin size={16} />
              </span>
            </div>
          </div>
        )}

        {/* Buy Button */}
        {balance < Number(snackPrices.prices[selectedSnack]?.cost || 0) ? (
          <Button
            variant="lime"
            fullWidth
            onClick={handleInsufficientBalance}
            haptic="medium"
          >
            {t('topUpBalance')}
          </Button>
        ) : (
          <Button
            variant="lime"
            fullWidth
            onClick={handleBuySnack}
            disabled={isProcessing}
            haptic="heavy"
          >
            {isProcessing
              ? t('processing')
              : t('buySnack', { price: formatNumber(snackPrices.prices[selectedSnack]?.cost || 0) })}
          </Button>
        )}
      </div>
    );
  };

  const renderRoiTab = () => {
    if (isLoading) {
      return <div className="text-center py-8 text-[#64748b]">{t('loading')}</div>;
    }

    if (!roiPrices) {
      return <div className="text-center py-8 text-[#64748b]">{t('loadError')}</div>;
    }

    const currentBoost = Number(roiPrices.current_boost);
    const maxBoost = Number(roiPrices.max_boost);

    if (currentBoost >= maxBoost) {
      return (
        <div className="p-4 rounded-xl bg-[#fbbf24]/10 border border-[#fbbf24]/30 text-center">
          <Image src="/pixelicons/roi.png" alt="ROI Max" width={48} height={48} className="mx-auto mb-2" />
          <p className="text-sm text-[#fbbf24]">{t('maxBoostReached')}</p>
          <p className="text-xs text-[#94a3b8] mt-1">{t('maxBoostDescription', { percent: maxBoost })}</p>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <p className="text-xs text-[#94a3b8] text-center">{t('roiDescription')}</p>

        {/* Current Boost Progress */}
        <div className="p-3 rounded-xl bg-[#1e293b]/40">
          <div className="flex justify-between text-xs mb-2">
            <span className="text-[#64748b]">{t('currentBoost')}</span>
            <span className="text-[#c7f464]">+{currentBoost}%</span>
          </div>
          <div className="h-2 bg-[#0d1220] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-[#c7f464] to-[#a3d62e] transition-all"
              style={{ width: `${(currentBoost / maxBoost) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs mt-1">
            <span className="text-[#64748b]">0%</span>
            <span className="text-[#64748b]">{maxBoost}% max</span>
          </div>
        </div>

        {/* ROI Options */}
        <div className="grid grid-cols-5 gap-1">
          {ROI_OPTIONS.map((option) => {
            const optionKey = `+${option}%`;
            const optionData = roiPrices.options[optionKey];
            if (!optionData) return null;
            const isSelected = selectedRoiOption === option;
            const canBuy = optionData.can_buy;
            return (
              <button
                key={option}
                onClick={() => { if (canBuy) { tap(); setSelectedRoiOption(option); } }}
                disabled={!canBuy}
                className={`p-2 rounded-lg border transition-all ${
                  !canBuy
                    ? 'bg-[#1e293b]/20 border-[#334155]/20 opacity-50'
                    : isSelected
                    ? 'bg-[#c7f464]/20 border-[#c7f464]/50'
                    : 'bg-[#1e293b]/40 border-[#334155]/30 hover:border-[#334155]/60'
                }`}
              >
                <span className={`text-sm font-medium ${canBuy ? 'text-[#f1f5f9]' : 'text-[#64748b]'}`}>
                  +{option}%
                </span>
              </button>
            );
          })}
        </div>

        {/* Selected Option Info */}
        {roiPrices.options[`+${selectedRoiOption}%`] && (
          <div className="p-4 rounded-xl bg-[#1e293b]/40 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('extraProfit')}</span>
              <span className="text-[#c7f464]">+${formatNumber(roiPrices.options[`+${selectedRoiOption}%`].extra_profit)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('newTotalBoost')}</span>
              <span className="text-[#f1f5f9]">+{currentBoost + Number(selectedRoiOption)}%</span>
            </div>
            <div className="h-px bg-[#334155]" />
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('cost')}</span>
              <span className="text-[#f1f5f9] inline-flex items-center gap-1">
                {formatNumber(roiPrices.options[`+${selectedRoiOption}%`].cost)} <XpetCoin size={16} />
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('netBenefit')}</span>
              <span className="text-[#c7f464] inline-flex items-center gap-1">
                +{formatNumber(roiPrices.options[`+${selectedRoiOption}%`].net_benefit)} <XpetCoin size={16} />
              </span>
            </div>
          </div>
        )}

        {/* Buy Button */}
        {balance < Number(roiPrices.options[`+${selectedRoiOption}%`]?.cost || 0) ? (
          <Button
            variant="lime"
            fullWidth
            onClick={handleInsufficientBalance}
            haptic="medium"
          >
            {t('topUpBalance')}
          </Button>
        ) : (
          <Button
            variant="lime"
            fullWidth
            onClick={handleBuyRoiBoost}
            disabled={isProcessing || !roiPrices.options[`+${selectedRoiOption}%`]?.can_buy}
            haptic="heavy"
          >
            {isProcessing
              ? t('processing')
              : t('buyRoiBoost', { percent: selectedRoiOption, price: formatNumber(roiPrices.options[`+${selectedRoiOption}%`]?.cost || 0) })}
          </Button>
        )}
      </div>
    );
  };

  const renderAutoClaimTab = () => {
    if (isLoading) {
      return <div className="text-center py-8 text-[#64748b]">{t('loading')}</div>;
    }

    if (!autoClaimStatus) {
      return <div className="text-center py-8 text-[#64748b]">{t('loadError')}</div>;
    }

    if (autoClaimStatus.is_active) {
      return (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#c7f464]/10 border border-[#c7f464]/30 text-center">
            <Image src="/pixelicons/autoclaim.png" alt="Auto-claim" width={48} height={48} className="mx-auto mb-2" />
            <p className="text-sm text-[#c7f464]">{t('autoClaimActive')}</p>
            <p className="text-xs text-[#94a3b8] mt-1">
              {t('expiresIn', { days: autoClaimStatus.days_remaining || 0 })}
            </p>
          </div>

          <div className="p-4 rounded-xl bg-[#1e293b]/40 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('totalClaims')}</span>
              <span className="text-[#f1f5f9]">{autoClaimStatus.total_claims || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('commissionPaid')}</span>
              <span className="text-[#f1f5f9] inline-flex items-center gap-1">
                {formatNumber(autoClaimStatus.total_commission || 0)} <XpetCoin size={16} />
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-[#64748b]">{t('commissionRate')}</span>
              <span className="text-[#94a3b8]">{autoClaimStatus.commission_percent}%</span>
            </div>
          </div>
        </div>
      );
    }

    const monthOptions = [1, 3, 6, 12];

    return (
      <div className="space-y-4">
        <p className="text-xs text-[#94a3b8] text-center">{t('autoClaimDescription')}</p>

        {/* Month Selection */}
        <div className="grid grid-cols-4 gap-2">
          {monthOptions.map((months) => {
            const cost = getAutoClaimCost(months);
            const discount = months > 1 ? Math.round((1 - cost / (5 * months)) * 100) : 0;
            const isSelected = selectedMonths === months;
            return (
              <button
                key={months}
                onClick={() => { tap(); setSelectedMonths(months); }}
                className={`p-3 rounded-xl border transition-all ${
                  isSelected
                    ? 'bg-[#c7f464]/20 border-[#c7f464]/50'
                    : 'bg-[#1e293b]/40 border-[#334155]/30 hover:border-[#334155]/60'
                }`}
              >
                <span className="text-sm font-medium text-[#f1f5f9] block">{months}</span>
                <span className="text-xs text-[#64748b]">{months === 1 ? t('month') : t('months')}</span>
                {discount > 0 && (
                  <span className="text-xs text-[#c7f464] block">-{discount}%</span>
                )}
              </button>
            );
          })}
        </div>

        {/* Info */}
        <div className="p-4 rounded-xl bg-[#1e293b]/40 space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-[#64748b]">{t('duration')}</span>
            <span className="text-[#f1f5f9]">{selectedMonths} {selectedMonths === 1 ? t('month') : t('months')}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-[#64748b]">{t('commissionRate')}</span>
            <span className="text-[#94a3b8]">{autoClaimStatus.commission_percent}% {t('perClaim')}</span>
          </div>
          <div className="h-px bg-[#334155]" />
          <div className="flex justify-between text-sm">
            <span className="text-[#64748b]">{t('totalCost')}</span>
            <span className="text-[#f1f5f9] inline-flex items-center gap-1">
              {formatNumber(getAutoClaimCost(selectedMonths))} <XpetCoin size={16} />
            </span>
          </div>
        </div>

        {/* Features */}
        <div className="p-3 rounded-xl bg-[#00f5d4]/10 border border-[#00f5d4]/20">
          <p className="text-xs text-[#00f5d4] font-medium mb-2">{t('features')}</p>
          <ul className="text-xs text-[#94a3b8] space-y-1">
            <li>• {t('feature1')}</li>
            <li>• {t('feature2')}</li>
            <li>• {t('feature3')}</li>
          </ul>
        </div>

        {/* Buy Button */}
        {balance < getAutoClaimCost(selectedMonths) ? (
          <Button
            variant="cyan"
            fullWidth
            onClick={handleInsufficientBalance}
            haptic="medium"
          >
            {t('topUpBalance')}
          </Button>
        ) : (
          <Button
            variant="cyan"
            fullWidth
            onClick={handleBuyAutoClaim}
            disabled={isProcessing}
            haptic="heavy"
          >
            {isProcessing
              ? t('processing')
              : t('buyAutoClaim', { price: formatNumber(getAutoClaimCost(selectedMonths)) })}
          </Button>
        )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={isProcessing ? undefined : handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm max-h-[85vh] rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-center p-6 pb-4">
          <h2 className="text-xl font-bold text-[#c7f464]">{t('title')}</h2>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            x
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="px-6 pb-4">
          <div className="flex gap-1 p-1 rounded-xl bg-[#1e293b]/40">
            <button
              onClick={() => { tap(); setActiveTab('snacks'); }}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1 ${
                activeTab === 'snacks'
                  ? 'bg-[#c7f464] text-[#0d1220]'
                  : 'text-[#94a3b8] hover:text-[#f1f5f9]'
              }`}
            >
              <Image src="/pixelicons/snack.png" alt="" width={16} height={16} /> {t('tabSnacks')}
            </button>
            <button
              onClick={() => { tap(); setActiveTab('roi'); }}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1 ${
                activeTab === 'roi'
                  ? 'bg-[#c7f464] text-[#0d1220]'
                  : 'text-[#94a3b8] hover:text-[#f1f5f9]'
              }`}
            >
              <Image src="/pixelicons/roi.png" alt="" width={16} height={16} /> {t('tabRoi')}
            </button>
            <button
              onClick={() => { tap(); setActiveTab('autoclaim'); }}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-1 ${
                activeTab === 'autoclaim'
                  ? 'bg-[#00f5d4] text-[#0d1220]'
                  : 'text-[#94a3b8] hover:text-[#f1f5f9]'
              }`}
            >
              <Image src="/pixelicons/autoclaim.png" alt="" width={16} height={16} /> {t('tabAutoClaim')}
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 pb-6 overflow-y-auto flex-1">
          {activeTab === 'snacks' && renderSnacksTab()}
          {activeTab === 'roi' && renderRoiTab()}
          {activeTab === 'autoclaim' && renderAutoClaimTab()}
        </div>

        {/* Balance Footer */}
        <div className="px-6 pb-6 pt-2 border-t border-[#1e293b]/50">
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#64748b]">{t('yourBalance')}</span>
            <span className="text-sm font-medium text-[#f1f5f9] inline-flex items-center gap-1">
              {formatNumber(balance)} <XpetCoin size={18} />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
