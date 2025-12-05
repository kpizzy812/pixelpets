'use client';

import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'bg-[#1e293b]/40 rounded-lg animate-pulse',
        className
      )}
    />
  );
}

// Pet Card Skeleton
export function PetCardSkeleton() {
  return (
    <div className="relative aspect-[3/4] rounded-3xl bg-gradient-to-br from-[#1e293b]/60 to-[#0d1220] border border-[#1e293b]/50 p-4 flex flex-col">
      {/* Level Badge */}
      <Skeleton className="absolute top-3 right-3 w-16 h-6 rounded-full" />

      {/* Pet Emoji Area */}
      <div className="flex-1 flex items-center justify-center">
        <Skeleton className="w-24 h-24 rounded-full" />
      </div>

      {/* Name */}
      <Skeleton className="w-2/3 h-5 mx-auto mb-2" />

      {/* Stats */}
      <div className="space-y-2 mb-4">
        <Skeleton className="w-full h-4" />
        <Skeleton className="w-3/4 h-4" />
      </div>

      {/* Button */}
      <Skeleton className="w-full h-12 rounded-xl" />
    </div>
  );
}

// Task Item Skeleton
export function TaskItemSkeleton() {
  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex items-center gap-4">
      {/* Icon */}
      <Skeleton className="w-12 h-12 rounded-xl flex-shrink-0" />

      {/* Content */}
      <div className="flex-1 space-y-2">
        <Skeleton className="w-3/4 h-4" />
        <Skeleton className="w-1/2 h-3" />
      </div>

      {/* Button */}
      <Skeleton className="w-20 h-9 rounded-lg flex-shrink-0" />
    </div>
  );
}

// Pet Type Card Skeleton (Shop - Grid)
export function PetTypeCardSkeleton() {
  return (
    <div className="rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex flex-col overflow-hidden">
      {/* Pet Image - Full width */}
      <Skeleton className="aspect-square" />

      {/* Content */}
      <div className="p-3">
        {/* Name */}
        <Skeleton className="w-2/3 h-4 mb-1" />

        {/* Stats */}
        <div className="flex justify-between mb-3">
          <Skeleton className="w-12 h-3" />
          <Skeleton className="w-16 h-3" />
        </div>

        {/* Button */}
        <Skeleton className="w-full h-8 rounded-xl" />
      </div>
    </div>
  );
}

// Referral Card Skeleton
export function RefCardSkeleton() {
  return (
    <div className="p-6 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
      <div className="space-y-4">
        <Skeleton className="w-1/3 h-5" />
        <Skeleton className="w-full h-12 rounded-xl" />
        <div className="flex gap-2">
          <Skeleton className="flex-1 h-10 rounded-xl" />
          <Skeleton className="flex-1 h-10 rounded-xl" />
        </div>
      </div>
    </div>
  );
}

// Stats Card Skeleton
export function StatsCardSkeleton() {
  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50">
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="text-center space-y-2">
            <Skeleton className="w-12 h-8 mx-auto" />
            <Skeleton className="w-16 h-3 mx-auto" />
          </div>
        ))}
      </div>
    </div>
  );
}

// Level Card Skeleton
export function LevelCardSkeleton() {
  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex items-center gap-4">
      <Skeleton className="w-10 h-10 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="w-1/3 h-4" />
        <Skeleton className="w-1/2 h-3" />
      </div>
      <Skeleton className="w-16 h-6 rounded-lg" />
    </div>
  );
}

// Balance Header Skeleton
export function BalanceHeaderSkeleton() {
  return (
    <div className="p-4 flex justify-between items-center">
      <div className="space-y-1">
        <Skeleton className="w-20 h-3" />
        <Skeleton className="w-28 h-6" />
      </div>
      <Skeleton className="w-10 h-10 rounded-full" />
    </div>
  );
}

// Home Screen Skeleton
export function HomeScreenSkeleton() {
  return (
    <div className="h-screen flex flex-col bg-[#050712] overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#1a0a2e] via-[#0a0f1a] to-[#050712] pointer-events-none" />

      <div className="relative flex flex-col h-full z-10">
        {/* Header */}
        <BalanceHeaderSkeleton />

        {/* Pet Cards */}
        <div className="flex-1 flex items-center justify-center px-8">
          <div className="w-full max-w-xs">
            <PetCardSkeleton />
          </div>
        </div>

        {/* Dots */}
        <div className="flex justify-center gap-2 pb-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="w-2 h-2 rounded-full" />
          ))}
        </div>

        {/* Bottom Nav */}
        <div className="h-20 bg-[#0d1220]/90 border-t border-[#1e293b]/50">
          <div className="flex justify-around items-center h-full px-6">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="w-12 h-12 rounded-xl" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Tasks Screen Skeleton
export function TasksScreenSkeleton() {
  return (
    <div className="p-4 space-y-4">
      {/* Balance */}
      <Skeleton className="w-full h-14 rounded-xl" />

      {/* Section Title */}
      <Skeleton className="w-24 h-4" />

      {/* Task Items */}
      {[1, 2, 3, 4].map((i) => (
        <TaskItemSkeleton key={i} />
      ))}
    </div>
  );
}

// Shop Screen Skeleton
export function ShopScreenSkeleton() {
  return (
    <div className="p-4 space-y-4">
      {/* Slots Info */}
      <Skeleton className="w-full h-12 rounded-xl" />

      {/* Pet Types Grid */}
      <div className="grid grid-cols-2 gap-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <PetTypeCardSkeleton key={i} />
        ))}
      </div>
    </div>
  );
}

// Referrals Screen Skeleton
export function ReferralsScreenSkeleton() {
  return (
    <div className="p-4 space-y-4">
      <RefCardSkeleton />
      <StatsCardSkeleton />
      <Skeleton className="w-32 h-4" />
      {[1, 2, 3, 4, 5].map((i) => (
        <LevelCardSkeleton key={i} />
      ))}
    </div>
  );
}
