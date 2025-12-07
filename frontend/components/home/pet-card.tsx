'use client';

import type { PetSlot } from '@/types/pet';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
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
  onBoosts?: () => void;
  onPetClick?: () => void;
  isFirstPet?: boolean;
}

export function PetCard({ slot, onTrain, onClaim, onShop, onUpgrade, onSell, onBoosts, onPetClick, isFirstPet = false }: PetCardProps) {
  const { tap } = useHaptic();
  const { pet } = slot;
  const countdown = useCountdown(pet?.trainingEndsAt);
  const t = useTranslations('home');

  // Empty slot
  if (!pet) {
    return (
      <div className="pet-card flex flex-col h-full items-center justify-center gap-6 py-8">
        {/* Pet Image Area */}
        <div className="w-[280px] h-[280px] rounded-3xl overflow-hidden">
          <img
            src="/pixelicons/no-pets.png"
            alt="Empty slot"
            className="w-full h-full object-cover"
          />
        </div>

        {/* Title */}
        <h3 className="text-xl font-bold text-[#f1f5f9] text-center">
          {isFirstPet ? t('emptySlot.firstPetTitle') : t('emptySlot.title')}
        </h3>

        {/* Description */}
        <p className="text-sm text-[#94a3b8] text-center max-w-[280px] leading-relaxed">
          {isFirstPet ? t('emptySlot.firstPetDescription') : t('emptySlot.description')}
        </p>

        {/* CTA */}
        <Button variant="cyan" fullWidth onClick={onShop}>
          <Icon name="shop" size={18} className="mr-2" />
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

  const getLevelNumber = (): number => {
    if (pet.level === 'BABY') return 1;
    if (pet.level === 'ADULT') return 2;
    return 3; // MYTHIC
  };

  return (
    <div className="pet-card flex flex-col h-full">
      {/* Top Pills */}
      <div className="flex justify-between items-start mb-4">
        {onUpgrade && pet.level !== 'MYTHIC' ? (
          <button
            onClick={() => { tap(); onUpgrade(); }}
            className="flex flex-col items-center gap-1 group"
          >
            <div className="flex items-center justify-center group-hover:scale-110 group-active:scale-95 transition-transform">
              <Icon name="levelup" size={56} />
            </div>
            <span className="text-xs font-medium text-[#c7f464]">{t('levelUp')}</span>
          </button>
        ) : (
          <div className="w-14 h-14" />
        )}
        {onBoosts && (
          <button
            onClick={() => { tap(); onBoosts(); }}
            className="flex flex-col items-center gap-1 group"
          >
            <div className="flex items-center justify-center group-hover:scale-110 group-active:scale-95 transition-transform">
              <Icon name="boosts" size={56} />
            </div>
            <span className="text-xs font-medium text-[#c7f464]">{t('boosts')}</span>
          </button>
        )}
      </div>

      {/* Pet Image Area - Clickable */}
      <div className="flex-1 flex items-center justify-center">
        <button
          onClick={() => { tap(); onPetClick?.(); }}
          className={`w-64 h-64 rounded-3xl bg-gradient-to-br ${getGradient()} border border-[#334155]/30 overflow-hidden shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-transform`}
        >
          <PetImage imageKey={pet.imageKey} level={pet.level} alt={pet.name} size={256} className="w-full h-full object-cover" />
        </button>
      </div>

      {/* Bottom Info */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-lg font-medium text-[#f1f5f9]">
              {pet.name}
            </span>
            <Image
              src={`/pixelicons/level${getLevelNumber()}.png`}
              alt={`Level ${getLevelNumber()}`}
              width={24}
              height={24}
            />
          </div>
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
