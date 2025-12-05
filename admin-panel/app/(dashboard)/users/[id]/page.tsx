"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Wallet, Users, PawPrint, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getUser, adjustBalance } from "@/lib/api/users";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";
import Link from "next/link";

export default function UserDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { isAdminOrAbove } = useAuthStore();
  const userId = Number(params.id);

  const [isAdjustDialogOpen, setIsAdjustDialogOpen] = useState(false);
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustReason, setAdjustReason] = useState("");

  const { data: user, isLoading } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => getUser(userId),
  });

  const adjustMutation = useMutation({
    mutationFn: (data: { amount: number; reason: string }) =>
      adjustBalance(userId, data),
    onSuccess: (result) => {
      toast({
        title: "Balance adjusted",
        description: `New balance: ${formatCurrency(result.new_balance)} XPET`,
      });
      queryClient.invalidateQueries({ queryKey: ["user", userId] });
      queryClient.invalidateQueries({ queryKey: ["users"] });
      setIsAdjustDialogOpen(false);
      setAdjustAmount("");
      setAdjustReason("");
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Failed to adjust balance",
        description: getErrorMessage(error),
      });
    },
  });

  const handleAdjustBalance = () => {
    const amount = parseFloat(adjustAmount);
    if (isNaN(amount) || amount === 0) {
      toast({
        variant: "destructive",
        title: "Invalid amount",
        description: "Please enter a valid non-zero amount",
      });
      return;
    }
    if (!adjustReason.trim()) {
      toast({
        variant: "destructive",
        title: "Reason required",
        description: "Please provide a reason for this adjustment",
      });
      return;
    }
    adjustMutation.mutate({ amount, reason: adjustReason });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Skeleton className="h-10 w-10" />
          <Skeleton className="h-8 w-48" />
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-48" />
          ))}
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">User not found</p>
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="outline" size="icon" asChild>
          <Link href="/users">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-bold">
            {user.first_name || user.username || "Anonymous User"}
            {user.last_name && ` ${user.last_name}`}
          </h1>
          {user.username && (
            <p className="text-muted-foreground">@{user.username}</p>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              User Info
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Telegram ID</p>
                <p className="font-mono">{user.telegram_id}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Language</p>
                <p className="uppercase">{user.language_code}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Ref Code</p>
                <p className="font-mono">{user.ref_code}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Referrer ID</p>
                <p>{user.referrer_id || "None"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Ref Levels</p>
                <Badge variant="secondary">{user.ref_levels_unlocked}/5</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Wallet */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              Wallet
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Current Balance</p>
              <p className="text-2xl font-bold">
                {formatCurrency(user.balance_xpet)} XPET
              </p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Deposited</p>
                <p className="font-medium text-green-600">
                  +{formatCurrency(user.total_deposited)} XPET
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Withdrawn</p>
                <p className="font-medium text-red-600">
                  -{formatCurrency(user.total_withdrawn)} XPET
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Claimed</p>
                <p className="font-medium">
                  {formatCurrency(user.total_claimed)} XPET
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Ref Earnings</p>
                <p className="font-medium">
                  {formatCurrency(user.total_ref_earned)} XPET
                </p>
              </div>
            </div>
            {isAdminOrAbove() && (
              <Dialog open={isAdjustDialogOpen} onOpenChange={setIsAdjustDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="w-full">Adjust Balance</Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Adjust Balance</DialogTitle>
                    <DialogDescription>
                      Add or subtract from the user&apos;s balance. Use negative values
                      to subtract.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label htmlFor="amount">Amount (XPET)</Label>
                      <Input
                        id="amount"
                        type="number"
                        step="0.01"
                        placeholder="e.g., 10 or -5"
                        value={adjustAmount}
                        onChange={(e) => setAdjustAmount(e.target.value)}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="reason">Reason</Label>
                      <Input
                        id="reason"
                        placeholder="Reason for adjustment"
                        value={adjustReason}
                        onChange={(e) => setAdjustReason(e.target.value)}
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() => setIsAdjustDialogOpen(false)}
                    >
                      Cancel
                    </Button>
                    <Button
                      onClick={handleAdjustBalance}
                      disabled={adjustMutation.isPending}
                    >
                      {adjustMutation.isPending ? "Adjusting..." : "Adjust"}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            )}
          </CardContent>
        </Card>

        {/* Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PawPrint className="h-5 w-5" />
              Activity
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Active Pets</p>
                <p className="text-2xl font-bold">{user.active_pets_count}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Referrals</p>
                <p className="text-2xl font-bold">{user.referrals_count}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Timestamps */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Timestamps
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Registered</p>
              <p>{formatDate(user.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Last Updated</p>
              <p>{formatDate(user.updated_at)}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
