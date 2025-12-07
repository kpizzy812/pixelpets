'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { PageLayout } from '@/components/layout/page-layout';
import { HallPetCard } from './hall-pet-card';
import { XpetCoin } from '@/components/ui/xpet-coin';
import { petsApi } from '@/lib/api';
import { formatNumber } from '@/lib/format';
import { useBackButton } from '@/hooks/use-back-button';
import type { HallOfFameEntry } from '@/types/api';

export function HallOfFameScreen() {
  const router = useRouter();

  useBackButton({
    show: true,
    onBack: () => {
      router.push('/');
      return true;
    },
  });
  const [pets, setPets] = useState<HallOfFameEntry[]>([]);
  const [totalEarned, setTotalEarned] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHallOfFame = async () => {
      try {
        const data = await petsApi.hallOfFame();
        setPets(data.pets);
        setTotalEarned(data.total_farmed_all_time);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load Hall of Fame');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHallOfFame();
  }, []);

  return (
    <PageLayout title="Hall of Fame">
      <div className="p-4 space-y-6">
        {/* Stats Header */}
        <div className="p-4 rounded-2xl bg-gradient-to-br from-[#fbbf24]/20 to-[#0d1220] border border-[#fbbf24]/30">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">*</span>
            <div>
              <h2 className="text-lg font-bold text-[#fbbf24]">Legendary Pets</h2>
              <p className="text-xs text-[#94a3b8]">Pets that reached their ROI cap</p>
            </div>
          </div>
          <div className="flex justify-between items-center pt-3 border-t border-[#334155]/50">
            <span className="text-sm text-[#64748b]">Total Earned</span>
            <span className="text-lg font-bold text-[#c7f464] inline-flex items-center gap-1">{formatNumber(totalEarned)} <XpetCoin size={22} /></span>
          </div>
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 rounded-2xl bg-[#1e293b]/40 animate-pulse" />
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-center">
            <span className="text-sm text-red-400">{error}</span>
          </div>
        )}

        {/* Pet List */}
        {!isLoading && !error && pets.length > 0 && (
          <div className="space-y-3">
            {pets.map((pet, index) => (
              <HallPetCard key={pet.id} pet={pet} rank={index + 1} />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && pets.length === 0 && (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block opacity-50">*</span>
            <h3 className="text-lg font-medium text-[#f1f5f9] mb-2">No Legends Yet</h3>
            <p className="text-sm text-[#64748b]">
              Train your pets until they reach their ROI cap to see them here!
            </p>
          </div>
        )}
      </div>
    </PageLayout>
  );
}
