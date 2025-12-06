'use client';

import type { ReactNode } from 'react';
import {
  Home,
  ShoppingCart,
  ClipboardList,
  Users,
  Coins,
  Circle,
  Gem,
  Egg,
  Sparkles,
  Star,
  Lock,
  Gift,
  Smartphone,
  MessageCircle,
  Check,
  CheckCircle,
  Skull,
  Wifi,
  Wrench,
  Inbox,
  AlertTriangle,
  X,
  Trophy,
  Wallet,
  Settings,
  ArrowUp,
  Share2,
  Copy,
  Dices,
  type LucideIcon,
  type LucideProps,
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Icon name to Lucide component mapping
const icons = {
  // Navigation
  home: Home,
  shop: ShoppingCart,
  tasks: ClipboardList,
  referrals: Users,

  // Currency/Networks
  coins: Coins,
  'network-bep20': Circle,
  'network-sol': Circle,
  'network-ton': Gem,

  // Pet/Game
  egg: Egg,
  sparkles: Sparkles,
  star: Star,

  // Status
  lock: Lock,
  gift: Gift,
  check: Check,
  'check-circle': CheckCircle,

  // Social/Tasks
  telegram: Smartphone,
  twitter: () => (
    <svg viewBox="0 0 24 24" fill="currentColor" className="w-full h-full">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
    </svg>
  ),
  discord: MessageCircle,

  // Error states
  error: Skull,
  network: Wifi,
  maintenance: Wrench,
  empty: Inbox,
  warning: AlertTriangle,

  // Actions
  close: X,
  upgrade: ArrowUp,
  share: Share2,
  copy: Copy,

  // Header
  trophy: Trophy,
  wallet: Wallet,
  settings: Settings,

  // Spin
  spin: Dices,
} as const;

export type IconName = keyof typeof icons;

interface IconProps extends Omit<LucideProps, 'ref'> {
  name: IconName;
  className?: string;
  size?: number;
}

export function Icon({ name, className, size = 24, ...props }: IconProps) {
  const IconComponent = icons[name];

  if (!IconComponent) {
    console.warn(`Icon "${name}" not found`);
    return null;
  }

  // Handle custom SVG components (like Twitter)
  if (typeof IconComponent === 'function' && !('displayName' in IconComponent)) {
    return (
      <span
        className={cn('inline-flex items-center justify-center', className)}
        style={{ width: size, height: size }}
      >
        {(IconComponent as () => ReactNode)()}
      </span>
    );
  }

  const LucideIconComponent = IconComponent as LucideIcon;

  return (
    <LucideIconComponent
      className={className}
      size={size}
      {...props}
    />
  );
}

// Export individual icons for direct import if needed
export {
  Home,
  ShoppingCart,
  ClipboardList,
  Users,
  Coins,
  Circle,
  Gem,
  Egg,
  Sparkles,
  Star,
  Lock,
  Gift,
  Smartphone,
  MessageCircle,
  Check,
  CheckCircle,
  Skull,
  Wifi,
  Wrench,
  Inbox,
  AlertTriangle,
  X,
  Trophy,
  Wallet,
  Settings,
  ArrowUp,
  Share2,
  Copy,
  Dices,
};
