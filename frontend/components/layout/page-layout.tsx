'use client';

import type { ReactNode } from 'react';

interface PageLayoutProps {
  children: ReactNode;
  title?: string;
  showBack?: boolean;
}

export function PageLayout({ children, title }: PageLayoutProps) {
  return (
    <div className="flex flex-col h-full overflow-hidden tg-safe-top tg-safe-bottom">
      {/* Header */}
      {title && (
        <div className="mx-4 mt-4 p-4 rounded-3xl bg-[#0d1220]/80 border border-[#1e293b]/50 backdrop-blur-sm">
          <h1 className="text-xl font-bold text-[#f1f5f9] text-center">{title}</h1>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto scrollbar-hide">
        {children}
      </div>
    </div>
  );
}
