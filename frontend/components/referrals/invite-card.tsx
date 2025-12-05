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
  refCode,
  onCopy,
  onShare,
  copied,
}: InviteCardProps) {
  return (
    <div className="p-5 rounded-2xl bg-gradient-to-br from-[#00f5d4]/10 to-[#1e293b]/50 border border-[#00f5d4]/20">
      <div className="text-center mb-4">
        <Icon name="gift" size={36} className="text-[#00f5d4] mx-auto mb-2" />
        <h2 className="text-lg font-bold text-[#f1f5f9]">Invite Friends</h2>
        <p className="text-sm text-[#94a3b8] mt-1">
          Earn up to 20% from their claims
        </p>
      </div>

      {/* Ref Code Display */}
      <div className="p-3 rounded-xl bg-[#0d1220]/80 border border-[#1e293b]/50 mb-4">
        <div className="text-center">
          <span className="text-xs text-[#64748b] uppercase tracking-wide">
            Your Code
          </span>
          <div className="text-xl font-mono font-bold text-[#00f5d4] mt-1">
            {refCode}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <Button variant="ghost" fullWidth onClick={onCopy}>
          {copied ? 'Copied!' : 'Copy Link'}
        </Button>
        <Button variant="cyan" fullWidth onClick={onShare}>
          Share
        </Button>
      </div>
    </div>
  );
}
