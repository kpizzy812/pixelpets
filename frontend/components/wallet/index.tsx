'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { useBalance, useGameStore } from '@/store/game-store';
import { walletApi } from '@/lib/api';
import { showSuccess, showError } from '@/lib/toast';
import { Icon, type IconName } from '@/components/ui/icon';
import type { NetworkType, DepositRequestResponse } from '@/types/api';

type WalletTab = 'deposit' | 'withdraw';

interface WalletModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const NETWORKS: { id: NetworkType; name: string; icon: IconName; color: string }[] = [
  { id: 'BEP20', name: 'BEP-20 (BSC)', icon: 'network-bep20', color: 'text-yellow-400' },
  { id: 'SOL', name: 'Solana', icon: 'network-sol', color: 'text-purple-400' },
  { id: 'TON', name: 'TON', icon: 'network-ton', color: 'text-cyan-400' },
];

export function WalletModal({ isOpen, onClose }: WalletModalProps) {
  const router = useRouter();
  const balance = useBalance();
  const updateBalance = useGameStore((state) => state.updateBalance);

  const [activeTab, setActiveTab] = useState<WalletTab>('deposit');
  const [selectedNetwork, setSelectedNetwork] = useState<NetworkType>('BEP20');
  const [amount, setAmount] = useState('');
  const [address, setAddress] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Deposit success state
  const [depositResult, setDepositResult] = useState<DepositRequestResponse | null>(null);

  if (!isOpen) return null;

  const resetForm = () => {
    setAmount('');
    setAddress('');
    setDepositResult(null);
  };

  const handleTabChange = (tab: WalletTab) => {
    setActiveTab(tab);
    resetForm();
  };

  const handleDeposit = async () => {
    const amountNum = Number(amount);
    if (!amount || amountNum < 5) {
      showError('Minimum deposit is 5 XPET');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await walletApi.createDeposit(selectedNetwork, amountNum);
      setDepositResult(result);
      showSuccess('Deposit request created!');
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to create deposit');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleWithdraw = async () => {
    const amountNum = Number(amount);
    if (!amount || amountNum < 5) {
      showError('Minimum withdrawal is 5 XPET');
      return;
    }
    if (!address) {
      showError('Please enter your wallet address');
      return;
    }
    if (amountNum > balance) {
      showError('Insufficient balance');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await walletApi.createWithdraw(selectedNetwork, address, amountNum);
      updateBalance(result.new_balance);
      showSuccess(`Withdrawal submitted! Fee: ${(result.fee ?? 0).toFixed(2)} XPET`);
      resetForm();
      onClose();
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to submit withdrawal');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGoToHistory = () => {
    onClose();
    router.push('/transactions');
  };

  const handleClose = () => {
    if (!isProcessing) {
      resetForm();
      onClose();
    }
  };

  const withdrawAmount = Number(amount) || 0;
  const fee = 1 + withdrawAmount * 0.02;
  const netAmount = Math.max(0, withdrawAmount - fee);

  // Show deposit address after successful request
  if (depositResult) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          onClick={handleClose}
        />

        <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl">
          <div className="text-center">
            <div className="w-16 h-16 rounded-full bg-[#00f5d4]/20 flex items-center justify-center mx-auto mb-4">
              <Icon name="check-circle" size={32} className="text-[#00f5d4]" />
            </div>

            <h2 className="text-xl font-bold text-[#f1f5f9] mb-2">Deposit Request Created</h2>

            <div className="p-4 rounded-2xl bg-[#1e293b]/40 mb-4">
              <div className="text-sm text-[#64748b] mb-1">Send exactly</div>
              <div className="text-2xl font-bold text-[#c7f464]">
                {depositResult.amount} XPET
              </div>
              <div className="text-sm text-[#64748b] mt-1">
                via {depositResult.network}
              </div>
            </div>

            {depositResult.deposit_address ? (
              <div className="mb-4">
                <div className="text-xs text-[#64748b] uppercase tracking-wide mb-2">
                  Deposit Address
                </div>
                <div className="p-3 rounded-xl bg-[#1e293b]/60 break-all text-sm text-[#f1f5f9] font-mono">
                  {depositResult.deposit_address}
                </div>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(depositResult.deposit_address!);
                    showSuccess('Address copied!');
                  }}
                  className="mt-2 text-sm text-[#00f5d4] hover:underline"
                >
                  Copy Address
                </button>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-[#fbbf24]/10 border border-[#fbbf24]/30 mb-4">
                <p className="text-sm text-[#fbbf24]">
                  Deposit address will be provided by admin. Check your request status in transaction history.
                </p>
              </div>
            )}

            <p className="text-xs text-[#64748b] mb-6">
              Your deposit will be credited within 24 hours after confirmation.
            </p>

            <div className="flex gap-3">
              <Button variant="ghost" fullWidth onClick={handleClose}>
                Close
              </Button>
              <Button variant="cyan" fullWidth onClick={() => setDepositResult(null)}>
                New Deposit
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-sm rounded-3xl bg-[#0d1220] border border-[#1e293b]/50 p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-[#f1f5f9]">Wallet</h2>
          <button
            onClick={handleClose}
            disabled={isProcessing}
            className="w-8 h-8 rounded-full bg-[#1e293b]/60 flex items-center justify-center text-[#64748b] hover:text-[#f1f5f9] transition-colors"
          >
            X
          </button>
        </div>

        {/* Balance */}
        <div className="p-4 rounded-2xl bg-[#1e293b]/40 mb-4 text-center">
          <span className="text-sm text-[#64748b]">Available Balance</span>
          <div className="text-2xl font-bold text-[#c7f464] mt-1">
            {(balance ?? 0).toFixed(2)} XPET
          </div>
        </div>

        {/* History Button */}
        <button
          onClick={handleGoToHistory}
          className="w-full p-3 rounded-xl bg-[#1e293b]/40 border border-[#334155]/50 flex items-center justify-between mb-4 hover:border-[#00f5d4]/30 transition-colors"
        >
          <div className="flex items-center gap-3">
            <Icon name="tasks" size={20} className="text-[#00f5d4]" />
            <span className="text-sm text-[#f1f5f9]">Transaction History</span>
          </div>
          <span className="text-[#64748b]">→</span>
        </button>

        {/* Tabs */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => handleTabChange('deposit')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'deposit'
                ? 'bg-[#00f5d4] text-[#050712]'
                : 'bg-[#1e293b]/60 text-[#94a3b8]'
            }`}
          >
            Deposit
          </button>
          <button
            onClick={() => handleTabChange('withdraw')}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeTab === 'withdraw'
                ? 'bg-[#00f5d4] text-[#050712]'
                : 'bg-[#1e293b]/60 text-[#94a3b8]'
            }`}
          >
            Withdraw
          </button>
        </div>

        {/* Network Selection */}
        <div className="mb-4">
          <label className="text-xs text-[#64748b] uppercase tracking-wide mb-2 block">
            Network
          </label>
          <div className="flex gap-2">
            {NETWORKS.map((network) => (
              <button
                key={network.id}
                onClick={() => setSelectedNetwork(network.id)}
                className={`flex-1 p-3 rounded-xl text-center transition-all ${
                  selectedNetwork === network.id
                    ? 'bg-[#00f5d4]/20 border border-[#00f5d4]/50'
                    : 'bg-[#1e293b]/40 border border-[#1e293b]/50'
                }`}
              >
                <Icon name={network.icon} size={24} className={network.color} />
                <div className="text-xs text-[#94a3b8] mt-1">{network.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Amount Input */}
        <div className="mb-4">
          <label className="text-xs text-[#64748b] uppercase tracking-wide mb-2 block">
            Amount (XPET)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Min: 5 XPET"
            className="w-full p-4 rounded-xl bg-[#1e293b]/40 border border-[#334155]/50 text-[#f1f5f9] placeholder-[#64748b] focus:outline-none focus:border-[#00f5d4]/50"
          />
        </div>

        {/* Withdraw-specific fields */}
        {activeTab === 'withdraw' && (
          <>
            <div className="mb-4">
              <label className="text-xs text-[#64748b] uppercase tracking-wide mb-2 block">
                Wallet Address
              </label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter your wallet address"
                className="w-full p-4 rounded-xl bg-[#1e293b]/40 border border-[#334155]/50 text-[#f1f5f9] placeholder-[#64748b] focus:outline-none focus:border-[#00f5d4]/50"
              />
            </div>

            {/* Fee Info */}
            <div className="p-4 rounded-xl bg-[#1e293b]/40 mb-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-[#64748b]">Amount</span>
                <span className="text-[#f1f5f9]">{withdrawAmount.toFixed(2)} XPET</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-[#64748b]">Fee ($1 + 2%)</span>
                <span className="text-red-400">-{fee.toFixed(2)} XPET</span>
              </div>
              <div className="h-px bg-[#334155]" />
              <div className="flex justify-between text-sm">
                <span className="text-[#64748b]">You Receive</span>
                <span className="text-[#c7f464] font-medium">{netAmount.toFixed(2)} XPET</span>
              </div>
            </div>
          </>
        )}

        {/* Action Button */}
        <Button
          variant={activeTab === 'deposit' ? 'cyan' : 'lime'}
          fullWidth
          onClick={activeTab === 'deposit' ? handleDeposit : handleWithdraw}
          disabled={isProcessing || Number(amount) < 5 || (activeTab === 'withdraw' && !address)}
        >
          {isProcessing
            ? 'Processing...'
            : activeTab === 'deposit'
            ? 'Create Deposit Request'
            : 'Submit Withdrawal'}
        </Button>

        {/* Info */}
        <p className="text-xs text-[#64748b] text-center mt-4">
          {activeTab === 'deposit'
            ? 'Deposits are processed manually within 24 hours.'
            : 'Withdrawals are processed manually within 24-48 hours.'}
        </p>
      </div>
    </div>
  );
}
