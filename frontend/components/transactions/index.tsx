'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { walletApi } from '@/lib/api';
import { Skeleton } from '@/components/ui/skeleton';
import { Icon } from '@/components/ui/icon';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { formatNumber } from '@/lib/format';
import type { Transaction, TxType } from '@/types/api';

const TX_TYPE_CONFIG: Record<TxType, { label: string; color: string; icon: string }> = {
  deposit: { label: 'Deposit', color: 'text-green-400', icon: '+' },
  withdraw: { label: 'Withdraw', color: 'text-red-400', icon: '-' },
  pet_buy: { label: 'Pet Purchase', color: 'text-orange-400', icon: '-' },
  pet_upgrade: { label: 'Pet Upgrade', color: 'text-orange-400', icon: '-' },
  sell_refund: { label: 'Pet Sold', color: 'text-green-400', icon: '+' },
  claim: { label: 'Training Reward', color: 'text-cyan-400', icon: '+' },
  ref_reward: { label: 'Referral Reward', color: 'text-purple-400', icon: '+' },
  task_reward: { label: 'Task Reward', color: 'text-yellow-400', icon: '+' },
  admin_adjust: { label: 'Admin Adjustment', color: 'text-gray-400', icon: '~' },
  withdraw_refund: { label: 'Withdrawal Refund', color: 'text-green-400', icon: '+' },
  spin_cost: { label: 'Spin Cost', color: 'text-orange-400', icon: '-' },
  spin_win: { label: 'Spin Win', color: 'text-yellow-400', icon: '+' },
};

const FILTER_OPTIONS: { value: TxType | 'ALL'; label: string }[] = [
  { value: 'ALL', label: 'All' },
  { value: 'deposit', label: 'Deposits' },
  { value: 'withdraw', label: 'Withdrawals' },
  { value: 'claim', label: 'Rewards' },
  { value: 'ref_reward', label: 'Referrals' },
];

function TransactionSkeleton() {
  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex items-center gap-4">
      <Skeleton className="w-10 h-10 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="w-24 h-4" />
        <Skeleton className="w-32 h-3" />
      </div>
      <Skeleton className="w-16 h-5" />
    </div>
  );
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
  });
}

interface TransactionItemProps {
  transaction: Transaction;
}

function TransactionItem({ transaction }: TransactionItemProps) {
  const config = TX_TYPE_CONFIG[transaction.type] || TX_TYPE_CONFIG.admin_adjust;
  const isPositive = config.icon === '+';

  return (
    <div className="p-4 rounded-2xl bg-[#0d1220]/80 border border-[#1e293b]/50 flex items-center gap-4">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
        isPositive ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
      }`}>
        {config.icon}
      </div>

      <div className="flex-1 min-w-0">
        <p className={`font-medium ${config.color}`}>{config.label}</p>
        <p className="text-xs text-[#64748b]">{formatDate(transaction.created_at)}</p>
      </div>

      <div className="text-right">
        <p className={`font-bold inline-flex items-center gap-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : '-'}{formatNumber(Math.abs(transaction.amount_xpet))} <XpetCoin size={18} />
        </p>
      </div>
    </div>
  );
}

export function TransactionsScreen() {
  const router = useRouter();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<TxType | 'ALL'>('ALL');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  const fetchTransactions = useCallback(async (pageNum: number, txType: TxType | 'ALL', append = false) => {
    setIsLoading(true);
    try {
      const response = await walletApi.transactions(
        pageNum,
        20,
        txType === 'ALL' ? undefined : txType
      );

      if (append) {
        setTransactions((prev) => [...prev, ...response.transactions]);
      } else {
        setTransactions(response.transactions);
      }

      setTotalPages(response.pages);
      setHasMore(pageNum < response.pages);
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    setPage(1);
    fetchTransactions(1, filter);
  }, [filter, fetchTransactions]);

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchTransactions(nextPage, filter, true);
  };

  const handleBack = () => {
    router.push('/');
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Gradient Background - fixed to cover full screen */}
      <div className="fixed inset-0 bg-gradient-to-b from-[#1a0a2e] via-[#0a0f1a] to-[#050712] pointer-events-none" />

      {/* Content */}
      <div className="relative flex flex-col h-full z-10 tg-safe-top tg-safe-bottom">
        {/* Header */}
        <div className="p-4">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={handleBack}
              className="w-10 h-10 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#94a3b8] hover:text-[#f1f5f9] transition-colors"
            >
              <Icon name="home" size={20} />
            </button>
            <h1 className="text-xl font-bold text-[#f1f5f9]">Transaction History</h1>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
            {FILTER_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => setFilter(option.value)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  filter === option.value
                    ? 'bg-[#00f5d4] text-[#050712]'
                    : 'bg-[#1e293b]/60 text-[#94a3b8] hover:bg-[#1e293b]'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Transaction List */}
        <div className="flex-1 overflow-y-auto scrollbar-hide px-4 pb-4">
          <div className="space-y-3">
            {isLoading && transactions.length === 0 ? (
              // Loading skeletons
              Array.from({ length: 5 }).map((_, i) => (
                <TransactionSkeleton key={i} />
              ))
            ) : transactions.length === 0 ? (
              // Empty state
              <div className="text-center py-12">
                <div className="w-16 h-16 rounded-full bg-[#1e293b]/40 flex items-center justify-center mx-auto mb-4">
                  <Icon name="empty" size={32} className="text-[#64748b]" />
                </div>
                <p className="text-[#64748b]">No transactions yet</p>
                <p className="text-xs text-[#475569] mt-1">
                  Your transaction history will appear here
                </p>
              </div>
            ) : (
              <>
                {transactions.map((tx) => (
                  <TransactionItem key={tx.id} transaction={tx} />
                ))}

                {/* Load More */}
                {hasMore && (
                  <button
                    onClick={handleLoadMore}
                    disabled={isLoading}
                    className="w-full p-4 rounded-2xl bg-[#1e293b]/40 border border-[#1e293b]/50 text-[#94a3b8] hover:bg-[#1e293b]/60 transition-colors"
                  >
                    {isLoading ? 'Loading...' : 'Load More'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
