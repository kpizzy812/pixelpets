'use client';

import Image from 'next/image';

interface XpetCoinProps {
  size?: number;
  className?: string;
}

export function XpetCoin({ size = 20, className = '' }: XpetCoinProps) {
  return (
    <Image
      src="/XPET.png"
      alt="XPET"
      width={size}
      height={size}
      className={`inline-block ${className}`}
    />
  );
}

interface XpetAmountProps {
  amount: number | string;
  size?: number;
  className?: string;
  showPlus?: boolean;
  showMinus?: boolean;
}

export function XpetAmount({
  amount,
  size = 20,
  className = '',
  showPlus = false,
  showMinus = false,
}: XpetAmountProps) {
  const prefix = showPlus ? '+' : showMinus ? '-' : '';
  return (
    <span className={`inline-flex items-center gap-1 ${className}`}>
      {prefix}{amount} <XpetCoin size={size} />
    </span>
  );
}
