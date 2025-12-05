'use client';

import Image from 'next/image';
import { cn } from '@/lib/utils';

interface PetImageProps {
  imageKey: string;
  alt?: string;
  size?: number;
  className?: string;
}

export function PetImage({ imageKey, alt = 'Pet', size = 64, className }: PetImageProps) {
  return (
    <Image
      src={`/pets/${imageKey}.png`}
      alt={alt}
      width={size}
      height={size}
      className={cn('object-contain', className)}
      priority
    />
  );
}

// Helper to get pet image URL for use in non-component contexts (like toasts)
export function getPetImageUrl(imageKey: string): string {
  return `/pets/${imageKey}.png`;
}
