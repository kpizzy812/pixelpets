'use client';

import { useState, useEffect } from 'react';

export function useCountdown(targetTime: number | undefined) {
  const [timeLeft, setTimeLeft] = useState(() => {
    if (!targetTime) return 0;
    return Math.max(0, targetTime - Date.now());
  });

  useEffect(() => {
    if (!targetTime) return;

    const interval = setInterval(() => {
      const remaining = Math.max(0, targetTime - Date.now());
      setTimeLeft(remaining);

      if (remaining === 0) {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [targetTime]);

  const hours = Math.floor(timeLeft / (1000 * 60 * 60));
  const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

  const formatted = `${hours.toString().padStart(2, '0')}:${minutes
    .toString()
    .padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

  const progress = targetTime
    ? 1 - timeLeft / (24 * 60 * 60 * 1000)
    : 0;

  return {
    timeLeft,
    formatted,
    progress: Math.min(1, Math.max(0, progress)),
    isComplete: timeLeft === 0,
  };
}
