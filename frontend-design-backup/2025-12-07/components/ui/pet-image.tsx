'use client';

import Image from 'next/image';
import type { PetLevel } from '@/types/pet';

// Map level names to numbers for image filenames
const LEVEL_TO_NUMBER: Record<PetLevel, number> = {
  BABY: 1,
  ADULT: 2,
  MYTHIC: 3,
};

interface PetImageProps {
  imageKey: string;
  level?: PetLevel;
  alt?: string;
  size?: number;
  className?: string;
}

export function PetImage({ imageKey, level = 'BABY', alt = 'Pet', size = 64, className }: PetImageProps) {
  const levelNumber = LEVEL_TO_NUMBER[level];

  return (
    <Image
      src={`/pets/${imageKey}${levelNumber}.png`}
      alt={alt}
      width={size}
      height={size}
      className={className}
      priority
    />
  );
}

// Helper to get pet image URL for use in non-component contexts (like toasts)
export function getPetImageUrl(imageKey: string, level: PetLevel = 'BABY'): string {
  const levelNumber = LEVEL_TO_NUMBER[level];
  return `/pets/${imageKey}${levelNumber}.png`;
}
