'use client';

import { useEffect, useState } from 'react';
import { Icon } from './icon';

interface AppLoaderProps {
  onComplete: () => void;
}

const LOAD_STEPS = [
  { label: 'Initializing Telegram...', weight: 15 },
  { label: 'Connecting to server...', weight: 25 },
  { label: 'Loading user data...', weight: 25 },
  { label: 'Fetching pets...', weight: 20 },
  { label: 'Preparing UI...', weight: 15 },
];

export function AppLoader({ onComplete }: AppLoaderProps) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    let cumulativeProgress = 0;
    let stepIndex = 0;

    const runStep = () => {
      if (stepIndex >= LOAD_STEPS.length) {
        // Fade out then complete
        setTimeout(() => {
          setIsVisible(false);
          setTimeout(onComplete, 300);
        }, 200);
        return;
      }

      setCurrentStep(stepIndex);
      const step = LOAD_STEPS[stepIndex];
      const targetProgress = cumulativeProgress + step.weight;

      // Animate progress smoothly
      const startProgress = cumulativeProgress;
      const duration = 200 + Math.random() * 300;
      const startTime = Date.now();

      const animate = () => {
        const elapsed = Date.now() - startTime;
        const easeProgress = Math.min(1, elapsed / duration);
        // Easing function for smooth animation
        const easedValue = 1 - Math.pow(1 - easeProgress, 3);
        const newProgress = startProgress + (targetProgress - startProgress) * easedValue;

        setProgress(newProgress);

        if (easeProgress < 1) {
          requestAnimationFrame(animate);
        } else {
          cumulativeProgress = targetProgress;
          stepIndex++;
          setTimeout(runStep, 100 + Math.random() * 150);
        }
      };

      requestAnimationFrame(animate);
    };

    // Start after a small delay
    const timer = setTimeout(runStep, 100);
    return () => clearTimeout(timer);
  }, [onComplete]);

  if (!isVisible) {
    return (
      <div className="fixed inset-0 z-[100] flex items-center justify-center opacity-0 transition-opacity duration-300" />
    );
  }

  return (
    <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center transition-opacity duration-300">
      {/* Background - transparent to show body background image */}
      <div className="absolute inset-0 pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center px-8 w-full max-w-xs">
        {/* Logo/Pet Animation */}
        <div className="relative mb-8">
          <div className="animate-bounce">
            <img
              src="/pixelicons/logo.png"
              alt="Pixel Pets"
              width={240}
              height={240}
              className="drop-shadow-[0_0_30px_rgba(147,51,234,0.7)]"
            />
          </div>
          {/* Glow effect - oval radial gradient */}
          <div
            className="absolute -z-10 animate-pulse"
            style={{
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '300px',
              height: '200px',
              background: 'radial-gradient(ellipse at center, rgba(147, 51, 234, 0.4) 0%, rgba(147, 51, 234, 0.1) 40%, transparent 70%)',
              filter: 'blur(20px)',
            }}
          />
        </div>

        {/* Title */}
        <h1 className="text-2xl font-bold text-[#f1f5f9] mb-2">
          Pixel Pets
        </h1>
        <p className="text-sm text-[#64748b] mb-8">
          Loading your adventure...
        </p>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-[#1e293b]/60 rounded-full overflow-hidden mb-3">
          <div
            className="h-full bg-gradient-to-r from-[#00f5d4] to-[#c7f464] rounded-full transition-all duration-100"
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Progress Text */}
        <div className="flex justify-between w-full text-xs">
          <span className="text-[#64748b]">
            {LOAD_STEPS[currentStep]?.label || 'Ready!'}
          </span>
          <span className="text-[#94a3b8] font-medium">
            {Math.round(progress)}%
          </span>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-1/4 left-8 opacity-20 animate-pulse">
          <Icon name="sparkles" size={36} className="text-[#00f5d4]" />
        </div>
        <div className="absolute top-1/3 right-8 opacity-20 animate-pulse delay-300">
          <Icon name="star" size={28} className="text-[#c7f464]" />
        </div>
        <div className="absolute bottom-1/4 left-12 opacity-20 animate-pulse delay-500">
          <Icon name="star" size={20} className="text-[#00f5d4]" />
        </div>
      </div>
    </div>
  );
}
