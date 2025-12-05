'use client';

import type { PetSlot } from '@/types/pet';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { ProgressBar } from '@/components/ui/progress-bar';
import { PetImage } from '@/components/ui/pet-image';
import { Icon } from '@/components/ui/icon';
import { useCountdown } from '@/hooks/use-countdown';
import { useHaptic } from '@/hooks/use-haptic';

interface PetCardProps {
  slot: PetSlot;
  onTrain: () => void;
  onClaim: () => void;
  onShop: () => void;
  onUpgrade?: () => void;
  onSell?: () => void;
}

export function PetCard({ slot, onTrain, onClaim, onShop, onUpgrade, onSell }: PetCardProps) {
  const { tap } = useHaptic();
  const { pet } = slot;
  const countdown = useCountdown(pet?.trainingEndsAt);
  const t = useTranslations('home');

  // Empty slot
  if (!pet) {
    return (
      <div className="pet-card flex flex-col h-full">
        {/* Top Pills */}
        <div className="flex justify-between items-start mb-4">
          <div className="px-3 py-1.5 rounded-xl bg-[#1e293b]/60 border border-[#334155]/30">
            <span className="text-xs text-[#64748b]">? LVL</span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-[#1e293b]/60 border border-[#334155]/30">
            <span className="text-xs text-[#64748b]">{t('unknown')}</span>
          </div>
        </div>

        {/* Pet Image Area */}
        <div className="flex-1 flex items-center justify-center">
          <div className="w-44 h-44 rounded-3xl bg-gradient-to-br from-[#1e293b]/80 to-[#0f172a]/80 border border-[#334155]/30 flex items-center justify-center">
            <span className="text-6xl opacity-30">❓</span>
          </div>
        </div>

        {/* Bottom Info */}
        <div className="flex justify-between items-center mb-4">
          <span className="text-lg font-medium text-[#64748b]">???</span>
          <div className="px-3 py-1.5 rounded-xl bg-[#1e293b]/60 border border-[#334155]/30">
            <span className="text-xs text-[#64748b]">+?.?%</span>
          </div>
        </div>

        {/* CTA */}
        <Button variant="lime" fullWidth onClick={onShop}>
          {t('toShop')}
        </Button>
      </div>
    );
  }

  // Owned pet
  const isTraining = pet.status === 'TRAINING';
  const isReady = pet.status === 'READY_TO_CLAIM' || (isTraining && countdown.isComplete);
  const isEvolved = pet.status === 'EVOLVED';
  const isIdle = pet.status === 'OWNED_IDLE';

  const getRarityColor = () => {
    switch (pet.rarity) {
      case 'Common': return 'text-[#94a3b8]';
      case 'Uncommon': return 'text-[#c7f464]';
      case 'Rare': return 'text-[#00f5d4]';
      case 'Epic': return 'text-[#a855f7]';
      case 'Legendary': return 'text-[#fbbf24]';
      case 'Mythic': return 'text-[#ff6b9d]';
      default: return 'text-[#94a3b8]';
    }
  };

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

  return (
    <div className="pet-card flex flex-col h-full">
      {/* Top Pills */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#1e293b]/60 border border-[#334155]/30">
            <span className="text-xs font-medium text-[#f1f5f9]">{pet.level}</span>
          </div>
          {onUpgrade && pet.level !== 'MYTHIC' && (
            <button
              onClick={() => { tap(); onUpgrade(); }}
              className="flex items-center justify-center w-8 h-8 rounded-xl bg-[#c7f464]/20 border border-[#c7f464]/40 hover:bg-[#c7f464]/30 transition-colors"
            >
              <Icon name="upgrade" size={16} className="text-[#c7f464]" />
            </button>
          )}
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-[#1e293b]/60 border border-[#334155]/30">
          <span className={`text-xs font-medium ${getRarityColor()}`}>{pet.rarity}</span>
        </div>
      </div>

      {/* Pet Image Area */}
      <div className="flex-1 flex items-center justify-center">
        <div className={`w-52 h-52 rounded-3xl bg-gradient-to-br ${getGradient()} border border-[#334155]/30 overflow-hidden shadow-lg`}>
          <PetImage imageKey={pet.imageKey} level={pet.level} alt={pet.name} size={208} className="w-full h-full object-cover" />
        </div>
      </div>

      {/* Bottom Info */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex flex-col">
          <span className="text-lg font-medium text-[#f1f5f9]">{pet.name}</span>
          <span className="text-xs text-[#94a3b8]">
            +${(pet.invested * pet.dailyRate / 100).toFixed(2)}/day
          </span>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-[#c7f464]/10 border border-[#c7f464]/20">
          <span className="text-xs font-semibold text-[#c7f464]">+{pet.dailyRate}%</span>
        </div>
      </div>

      {/* CTA / Progress */}
      {isTraining && !countdown.isComplete ? (
        <div className="space-y-3">
          <ProgressBar progress={countdown.progress} />
          <div className="text-center">
            <span className="text-sm font-mono text-[#94a3b8]">{countdown.formatted}</span>
          </div>
        </div>
      ) : isReady ? (
        <Button variant="amber" fullWidth onClick={onClaim} haptic="heavy">
          {t('claimLoot')}
        </Button>
      ) : isEvolved ? (
        <Button variant="disabled" fullWidth disabled>
          {t('evolved')}
        </Button>
      ) : isIdle ? (
        <Button variant="cyan" fullWidth onClick={onTrain}>
          {t('train24h')}
        </Button>
      ) : null}
    </div>
  );
}
