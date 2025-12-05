'use client';

import { useState, useEffect } from 'react';
import { PageLayout } from '@/components/layout/page-layout';
import { TaskItem } from './task-item';
import { TaskItemSkeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/error-state';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { useGameStore, useBalance } from '@/store/game-store';
import { showReward, showError } from '@/lib/toast';
import { formatNumber } from '@/lib/format';
import type { Task } from '@/types/api';

export function TasksScreen() {
  const balance = useBalance();
  const { tasks, tasksLoading, fetchTasks, checkTask } = useGameStore();

  const [checkingId, setCheckingId] = useState<number | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleGo = (task: Task) => {
    if (task.link) {
      window.open(task.link, '_blank');
    }
  };

  const handleCheck = async (taskId: number) => {
    setCheckingId(taskId);

    try {
      const result = await checkTask(taskId);
      if (result.success) {
        showReward(result.reward);
      } else {
        showError('Task not completed yet');
      }
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to check task');
    } finally {
      setCheckingId(null);
    }
  };

  const activeTasks = tasks.filter((t) => !t.is_completed);
  const completedTasks = tasks.filter((t) => t.is_completed);

  return (
    <PageLayout title="Tasks">
      <div className="p-4 space-y-6">
        {/* Balance Display */}
        <div className="p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex justify-between items-center">
          <span className="text-sm text-[#94a3b8]">Your Balance</span>
          <span className="text-sm font-medium text-[#c7f464] inline-flex items-center gap-1">
            {formatNumber(balance)} <XpetCoin size={18} />
          </span>
        </div>

        {tasksLoading && tasks.length === 0 ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <TaskItemSkeleton key={i} />
            ))}
          </div>
        ) : (
          <>
            {/* Active Tasks */}
            {activeTasks.length > 0 && (
              <div className="space-y-3">
                <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wide">
                  Available
                </h2>
                {activeTasks.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onGo={() => handleGo(task)}
                    onCheck={() => handleCheck(task.id)}
                    isChecking={checkingId === task.id}
                  />
                ))}
              </div>
            )}

            {/* Completed Tasks */}
            {completedTasks.length > 0 && (
              <div className="space-y-3">
                <h2 className="text-sm font-medium text-[#64748b] uppercase tracking-wide">
                  Completed
                </h2>
                {completedTasks.map((task) => (
                  <TaskItem
                    key={task.id}
                    task={task}
                    onGo={() => handleGo(task)}
                    onCheck={() => {}}
                    isChecking={false}
                  />
                ))}
              </div>
            )}

            {/* Empty State */}
            {tasks.length === 0 && (
              <EmptyState
                icon="tasks"
                title="No Tasks Available"
                message="Check back later for new tasks to complete and earn XPET!"
              />
            )}
          </>
        )}
      </div>
    </PageLayout>
  );
}
