"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Users,
  Wallet,
  ArrowDownToLine,
  ArrowUpFromLine,
  PawPrint,
  Trophy,
  Coins,
  UserPlus,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboardStats } from "@/lib/api/stats";
import { formatCurrency } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

function StatCard({
  title,
  value,
  icon: Icon,
  description,
  variant = "default",
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  description?: string;
  variant?: "default" | "success" | "warning" | "destructive";
}) {
  const variantStyles = {
    default: "text-muted-foreground",
    success: "text-success",
    warning: "text-warning",
    destructive: "text-destructive",
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 ${variantStyles[variant]}`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

function StatCardSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-4" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-32 mb-1" />
        <Skeleton className="h-3 w-20" />
      </CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: getDashboardStats,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Users Stats */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Users</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Users"
            value={stats?.total_users.toLocaleString() ?? 0}
            icon={Users}
            description="All registered users"
          />
          <StatCard
            title="New Today"
            value={stats?.new_users_today ?? 0}
            icon={UserPlus}
            description="Registered today"
            variant="success"
          />
          <StatCard
            title="New This Week"
            value={stats?.new_users_week ?? 0}
            icon={UserPlus}
            description="Registered this week"
          />
          <StatCard
            title="Active Today"
            value={stats?.active_users_today ?? 0}
            icon={Users}
            description="Active users today"
            variant="success"
          />
        </div>
      </div>

      {/* Financial Stats */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Finances</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Balance"
            value={`${formatCurrency(stats?.total_balance_xpet ?? 0)} XPET`}
            icon={Wallet}
            description="All users combined"
          />
          <StatCard
            title="Total Deposited"
            value={`${formatCurrency(stats?.total_deposited ?? 0)} XPET`}
            icon={ArrowDownToLine}
            variant="success"
          />
          <StatCard
            title="Total Withdrawn"
            value={`${formatCurrency(stats?.total_withdrawn ?? 0)} XPET`}
            icon={ArrowUpFromLine}
            variant="warning"
          />
          <StatCard
            title="Total Claimed"
            value={`${formatCurrency(stats?.total_claimed_xpet ?? 0)} XPET`}
            icon={Coins}
          />
        </div>
      </div>

      {/* Pending Requests */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Pending Requests</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Pending Deposits"
            value={stats?.pending_deposits_count ?? 0}
            icon={ArrowDownToLine}
            description={`${formatCurrency(stats?.pending_deposits_amount ?? 0)} XPET`}
            variant={stats?.pending_deposits_count ? "warning" : "default"}
          />
          <StatCard
            title="Pending Withdrawals"
            value={stats?.pending_withdrawals_count ?? 0}
            icon={ArrowUpFromLine}
            description={`${formatCurrency(stats?.pending_withdrawals_amount ?? 0)} XPET`}
            variant={stats?.pending_withdrawals_count ? "warning" : "default"}
          />
        </div>
      </div>

      {/* Game Stats */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Game</h2>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Active Pets"
            value={stats?.total_pets_active ?? 0}
            icon={PawPrint}
            description="Currently training"
          />
          <StatCard
            title="Evolved Pets"
            value={stats?.total_pets_evolved ?? 0}
            icon={Trophy}
            description="In Hall of Fame"
            variant="success"
          />
          <StatCard
            title="Referral Rewards"
            value={`${formatCurrency(stats?.total_ref_rewards_paid ?? 0)} XPET`}
            icon={Users}
            description="Total paid"
          />
          <StatCard
            title="Task Rewards"
            value={`${formatCurrency(stats?.total_task_rewards_paid ?? 0)} XPET`}
            icon={Coins}
            description="Total paid"
          />
        </div>
      </div>
    </div>
  );
}
