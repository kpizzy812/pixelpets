'use client';

import { useState, useRef, useEffect } from 'react';
import type { PetSlot } from '@/types/pet';
import { PetCard } from './pet-card';

interface PetCarouselProps {
  slots: PetSlot[];
  onTrain: (index: number) => void;
  onClaim: (index: number) => void;
  onShop: () => void;
  onUpgrade?: (index: number) => void;
  onSell?: (index: number) => void;
  onBoosts?: (index: number) => void;
  onPetClick?: (index: number) => void;
}

export function PetCarousel({ slots, onTrain, onClaim, onShop, onUpgrade, onSell, onBoosts, onPetClick }: PetCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Check if user has any pets
  const hasPets = slots.some(slot => slot.pet !== null);

  useEffect(() => {
    const container = scrollRef.current;
    if (!container) return;

    const handleScroll = () => {
      const scrollLeft = container.scrollLeft;
      const cardWidth = container.offsetWidth * 0.85;
      const gap = 16;
      const index = Math.round(scrollLeft / (cardWidth + gap));
      setActiveIndex(Math.min(Math.max(0, index), slots.length - 1));
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [slots.length]);

  // Scroll to center card on mount (only if more than 1 slot)
  useEffect(() => {
    const container = scrollRef.current;
    if (!container || slots.length <= 1) return;

    const cardWidth = container.offsetWidth * 0.85;
    const gap = 16;
    // Scroll to middle slot
    const middleIndex = Math.floor(slots.length / 2);
    container.scrollLeft = (cardWidth + gap) * middleIndex;
    setActiveIndex(middleIndex);
  }, [slots.length]);

  // Don't render anything if no slots
  if (slots.length === 0) {
    return (
      <div className="flex flex-col flex-1 min-h-0 items-center justify-center">
        <div className="text-[#64748b] text-sm">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Carousel */}
      <div
        ref={scrollRef}
        className="flex-1 flex gap-4 overflow-x-auto snap-x snap-mandatory scrollbar-hide px-[7.5%] py-2"
        style={{ scrollPaddingLeft: '7.5%', scrollPaddingRight: '7.5%' }}
      >
        {slots.map((slot) => (
          <div
            key={slot.index}
            className="w-[85%] shrink-0 snap-center"
          >
            <div className="h-full p-5 rounded-[32px] bg-[#0d1220]/90 border border-[#1e293b]/50 backdrop-blur-sm shadow-[0_0_40px_rgba(0,0,0,0.3)]">
              <PetCard
                slot={slot}
                onTrain={() => onTrain(slot.index)}
                onClaim={() => onClaim(slot.index)}
                onShop={onShop}
                onUpgrade={onUpgrade ? () => onUpgrade(slot.index) : undefined}
                onSell={onSell ? () => onSell(slot.index) : undefined}
                onBoosts={onBoosts ? () => onBoosts(slot.index) : undefined}
                onPetClick={onPetClick ? () => onPetClick(slot.index) : undefined}
                isFirstPet={!hasPets}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Pagination Dots (only show if more than 1 slot) */}
      {slots.length > 1 && (
        <div className="flex justify-center gap-2 py-3">
          {slots.map((_, i) => (
            <div
              key={i}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                i === activeIndex
                  ? 'bg-[#00f5d4] shadow-[0_0_8px_rgba(0,245,212,0.6)]'
                  : 'bg-[#334155]'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
