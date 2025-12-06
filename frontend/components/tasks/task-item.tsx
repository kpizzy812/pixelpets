'use client';

import { Button } from '@/components/ui/button';
import { Icon, type IconName } from '@/components/ui/icon';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useHaptic } from '@/hooks/use-haptic';
import type { Task } from '@/types/api';
import Image from 'next/image';

interface TaskItemProps {
  task: Task;
  onGo: () => void;
  onCheck: () => void;
  isChecking: boolean;
}

const TASK_ICONS: Record<string, IconName> = {
  telegram: 'telegram',
  twitter: 'twitter',
  discord: 'discord',
  referral: 'referrals',
  default: 'sparkles',
};

export function TaskItem({ task, onGo, onCheck, isChecking }: TaskItemProps) {
  const { tap } = useHaptic();
  const icon = TASK_ICONS[task.task_type] || TASK_ICONS.default;

  const handleGo = () => {
    tap();
    onGo();
  };

  return (
    <div
      className={`p-4 rounded-2xl bg-[#0d1220]/90 border transition-all ${
        task.is_completed
          ? 'border-[#334155]/30 opacity-60'
          : 'border-[#1e293b]/50'
      }`}
    >
      <div className="flex items-center gap-4">
        {/* Icon */}
        <div className="w-12 h-12 rounded-xl bg-[#1e293b]/60 flex items-center justify-center">
          {task.is_completed ? (
            <Icon name="checkbox" size={28} />
          ) : task.task_type === 'telegram' ? (
            <Image src="/tg.svg" alt="Telegram" width={24} height={24} />
          ) : (
            <Icon name={icon} size={24} className="text-[#94a3b8]" />
          )}
        </div>

        {/* Info */}
        <div className="flex-1">
          <div className="text-base font-medium text-[#f1f5f9]">{task.title}</div>
          <div className="text-sm text-[#c7f464] inline-flex items-center gap-1">+{task.reward_xpet} <XpetCoin size={18} /></div>
        </div>

        {/* Action */}
        {task.is_completed ? (
          <span className="text-sm text-[#64748b]">Done</span>
        ) : task.link ? (
          <div className="flex gap-2">
            <Button variant="ghost" onClick={handleGo} className="text-xs px-3 py-2" haptic="light">
              Go
            </Button>
            <Button
              variant="cyan"
              onClick={onCheck}
              disabled={isChecking}
              className="text-xs px-3 py-2"
            >
              {isChecking ? '...' : 'Check'}
            </Button>
          </div>
        ) : (
          <Button
            variant="cyan"
            onClick={onCheck}
            disabled={isChecking}
            className="text-xs px-4 py-2"
          >
            {isChecking ? '...' : 'Check'}
          </Button>
        )}
      </div>
    </div>
  );
}
