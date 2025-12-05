'use client';

import { useRef, useEffect } from 'react';
import type { SpinReward } from '@/types/api';

interface WheelProps {
  rewards: SpinReward[];
  isSpinning: boolean;
  winningIndex: number | null;
  onSpinEnd?: () => void;
}

export function Wheel({ rewards, isSpinning, winningIndex, onSpinEnd }: WheelProps) {
  const wheelRef = useRef<HTMLDivElement>(null);
  const hasSpunRef = useRef(false);

  useEffect(() => {
    if (!wheelRef.current || rewards.length === 0) return;

    if (isSpinning && winningIndex !== null && !hasSpunRef.current) {
      hasSpunRef.current = true;
      const segmentAngle = 360 / rewards.length;
      // Spin multiple rotations + land on winning segment
      // Add half segment to center on the reward
      const targetAngle = 360 * 5 + (360 - winningIndex * segmentAngle - segmentAngle / 2);

      wheelRef.current.style.transition = 'transform 4s cubic-bezier(0.17, 0.67, 0.12, 0.99)';
      wheelRef.current.style.transform = `rotate(${targetAngle}deg)`;

      const timeout = setTimeout(() => {
        hasSpunRef.current = false;
        onSpinEnd?.();
      }, 4000);

      return () => clearTimeout(timeout);
    }

    if (!isSpinning && !hasSpunRef.current) {
      // Reset wheel position without animation
      wheelRef.current.style.transition = 'none';
      wheelRef.current.style.transform = 'rotate(0deg)';
    }
  }, [isSpinning, winningIndex, rewards.length, onSpinEnd]);

  if (rewards.length === 0) {
    return (
      <div className="w-72 h-72 rounded-full bg-[#1a2235] flex items-center justify-center">
        <span className="text-[#64748b]">Loading...</span>
      </div>
    );
  }

  const segmentAngle = 360 / rewards.length;

  return (
    <div className="relative w-72 h-72">
      {/* Pointer */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-2 z-10">
        <div className="w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-t-[20px] border-t-[#c7f464] drop-shadow-lg" />
      </div>

      {/* Wheel */}
      <div
        ref={wheelRef}
        className="w-full h-full rounded-full overflow-hidden relative shadow-2xl"
        style={{
          background: `conic-gradient(${rewards
            .map((r, i) => `${r.color} ${i * segmentAngle}deg ${(i + 1) * segmentAngle}deg`)
            .join(', ')})`,
        }}
      >
        {/* Segment labels */}
        {rewards.map((reward, index) => {
          const rotation = index * segmentAngle + segmentAngle / 2;
          return (
            <div
              key={reward.id}
              className="absolute w-full h-full flex items-center justify-center"
              style={{
                transform: `rotate(${rotation}deg)`,
              }}
            >
              <div
                className="absolute flex flex-col items-center"
                style={{
                  transform: `translateY(-90px) rotate(0deg)`,
                }}
              >
                <span className="text-2xl">{reward.emoji}</span>
                <span className="text-xs font-bold text-white drop-shadow-md">
                  {reward.reward_type === 'nothing' ? '' : reward.label}
                </span>
              </div>
            </div>
          );
        })}

        {/* Center circle */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full bg-[#0d1220] border-4 border-[#c7f464] flex items-center justify-center shadow-lg">
          <span className="text-2xl">🎰</span>
        </div>
      </div>

      {/* Outer ring */}
      <div className="absolute inset-0 rounded-full border-4 border-[#c7f464]/30 pointer-events-none" />
    </div>
  );
}
