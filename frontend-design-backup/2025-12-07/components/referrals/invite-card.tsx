'use client';

import { Button } from '@/components/ui/button';
import { Icon } from '@/components/ui/icon';

interface InviteCardProps {
  refLink: string;
  refCode: string;
  onCopy: () => void;
  onShare: () => void;
  copied: boolean;
}

export function InviteCard({
  refLink,
  refCode,
  onCopy,
  onShare,
  copied,
}: InviteCardProps) {
  return (
    <div className="p-4 rounded-2xl bg-gradient-to-br from-[#00f5d4]/10 to-[#1e293b]/50 border border-[#00f5d4]/20">
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-[#00f5d4]/20 flex items-center justify-center">
          <Icon name="gift" size={20} className="text-[#00f5d4]" />
        </div>
        <div>
          <h2 className="text-base font-bold text-[#f1f5f9]">Invite Friends</h2>
          <p className="text-xs text-[#94a3b8]">Earn up to 20% from their claims</p>
        </div>
      </div>

      {/* Ref Link Display */}
      <div className="p-2.5 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 mb-3">
        <div className="flex items-center justify-between gap-2">
          <div className="flex-1 min-w-0">
            <span className="text-[10px] text-[#64748b] uppercase tracking-wide block mb-0.5">
              Your referral link
            </span>
            <div className="text-xs font-mono text-[#00f5d4] truncate">
              {refLink}
            </div>
          </div>
          <button
            onClick={onCopy}
            className="flex-shrink-0 p-2 rounded-lg bg-[#1e293b]/60 hover:bg-[#1e293b] transition-colors"
          >
            <Icon
              name={copied ? 'check' : 'copy'}
              size={16}
              className={copied ? 'text-[#c7f464]' : 'text-[#94a3b8]'}
            />
          </button>
        </div>
      </div>

      {/* Share Button */}
      <Button variant="cyan" fullWidth onClick={onShare}>
        <span className="inline-flex items-center gap-2">
          <Icon name="share" size={16} />
          Share with Friends
        </span>
      </Button>
    </div>
  );
}
