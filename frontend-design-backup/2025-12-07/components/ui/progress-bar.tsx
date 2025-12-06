'use client';

interface ProgressBarProps {
  progress: number; // 0 to 1
  className?: string;
}

export function ProgressBar({ progress, className = '' }: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, progress * 100));

  return (
    <div className={`h-2 bg-[#1e293b] rounded-full overflow-hidden ${className}`}>
      <div
        className="h-full bg-gradient-to-r from-[#00f5d4] to-[#c7f464] rounded-full transition-all duration-500"
        style={{ width: `${percentage}%` }}
      />
    </div>
  );
}
