'use client';

import { ButtonHTMLAttributes, forwardRef, useCallback } from 'react';
import { useHaptic } from '@/hooks/use-haptic';

type ButtonVariant = 'lime' | 'cyan' | 'amber' | 'ghost' | 'disabled';
type HapticStyle = 'light' | 'medium' | 'heavy' | 'none';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  haptic?: HapticStyle;
}

const variantStyles: Record<ButtonVariant, string> = {
  lime: 'bg-[#c7f464] text-[#050712] hover:bg-[#d4f87a] shadow-[0_0_20px_rgba(199,244,100,0.3)]',
  cyan: 'bg-[#00f5d4] text-[#050712] hover:bg-[#33f7dd] shadow-[0_0_20px_rgba(0,245,212,0.3)]',
  amber: 'bg-[#fbbf24] text-[#050712] hover:bg-[#fcd34d] shadow-[0_0_20px_rgba(251,191,36,0.3)]',
  ghost: 'bg-transparent border border-[#1e293b] text-[#94a3b8] hover:border-[#334155] hover:text-[#f1f5f9]',
  disabled: 'bg-[#1e293b] text-[#64748b] cursor-not-allowed',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'lime', fullWidth, className = '', children, disabled, haptic = 'medium', onClick, ...props }, ref) => {
    const { impact } = useHaptic();

    const handleClick = useCallback(
      (e: React.MouseEvent<HTMLButtonElement>) => {
        if (!disabled && haptic !== 'none') {
          impact(haptic);
        }
        onClick?.(e);
      },
      [disabled, haptic, impact, onClick]
    );

    const baseStyles =
      'px-6 py-3 rounded-2xl font-semibold text-sm uppercase tracking-wide transition-all duration-200 active:scale-[0.98]';
    const widthStyles = fullWidth ? 'w-full' : '';
    const variantStyle = disabled ? variantStyles.disabled : variantStyles[variant];

    return (
      <button
        ref={ref}
        disabled={disabled}
        className={`${baseStyles} ${widthStyles} ${variantStyle} ${className}`}
        onClick={handleClick}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
