'use client';

import { useRef, useEffect } from 'react';
import Image from 'next/image';
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
      {/* Outer golden ring with glow */}
      <div
        className="absolute -inset-2 rounded-full pointer-events-none"
        style={{
          background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 25%, #FFD700 50%, #B8860B 75%, #FFD700 100%)',
          boxShadow: '0 0 20px rgba(255, 215, 0, 0.4), inset 0 0 10px rgba(0,0,0,0.3)',
        }}
      />

      {/* Inner dark ring */}
      <div className="absolute -inset-1 rounded-full bg-[#1a1a2e] pointer-events-none" />

      {/* Pointer */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-3 z-10">
        <div
          className="w-0 h-0 border-l-[14px] border-l-transparent border-r-[14px] border-r-transparent border-t-[24px] border-t-[#FFD700]"
          style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.5))' }}
        />
      </div>

      {/* Wheel */}
      <div
        ref={wheelRef}
        className="w-full h-full rounded-full overflow-hidden relative"
        style={{
          background: `conic-gradient(${rewards
            .map((r, i) => `${r.color} ${i * segmentAngle}deg ${(i + 1) * segmentAngle}deg`)
            .join(', ')})`,
          boxShadow: 'inset 0 0 30px rgba(0,0,0,0.3)',
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
                className="absolute flex flex-col items-center gap-0.5"
                style={{
                  transform: `translateY(-85px) rotate(0deg)`,
                }}
              >
                <Image
                  src="/XPET.png"
                  alt="XPET"
                  width={24}
                  height={24}
                  className="drop-shadow-lg"
                />
                <span
                  className="text-xs font-bold text-white"
                  style={{ textShadow: '0 1px 2px rgba(0,0,0,0.8)' }}
                >
                  {reward.label}
                </span>
              </div>
            </div>
          );
        })}

        {/* Center circle */}
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #1a1a2e 0%, #0d0d1a 100%)',
            border: '3px solid #FFD700',
            boxShadow: '0 0 15px rgba(255, 215, 0, 0.3), inset 0 0 10px rgba(0,0,0,0.5)',
          }}
        >
          <Image
            src="/XPET.png"
            alt="XPET"
            width={32}
            height={32}
            className="drop-shadow-lg"
          />
        </div>
      </div>

      {/* Decorative dots on rim */}
      {[...Array(16)].map((_, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-[#FFD700]"
          style={{
            top: '50%',
            left: '50%',
            transform: `rotate(${i * 22.5}deg) translateY(-142px) translate(-50%, -50%)`,
            boxShadow: '0 0 4px rgba(255, 215, 0, 0.6)',
          }}
        />
      ))}
    </div>
  );
}
