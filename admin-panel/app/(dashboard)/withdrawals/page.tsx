"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  Loader2,
  Copy,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getWithdrawals, withdrawalAction } from "@/lib/api/withdrawals";
import { formatCurrency, formatDate, truncateAddress } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";
import { Withdrawal, WithdrawalStatus, NetworkType } from "@/types";
import Link from "next/link";

const statusColors: Record<WithdrawalStatus, "default" | "success" | "destructive"> = {
  pending: "default",
  completed: "success",
  rejected: "destructive",
};

const networkColors: Record<NetworkType, string> = {
  "BEP-20": "bg-yellow-100 text-yellow-800",
  "Solana": "bg-purple-100 text-purple-800",
  "TON": "bg-blue-100 text-blue-800",
};

export default function WithdrawalsPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isAdminOrAbove } = useAuthStore();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [networkFilter, setNetworkFilter] = useState<string>("all");
  const [actionDialog, setActionDialog] = useState<{
    withdrawal: Withdrawal;
    action: "complete" | "reject";
  } | null>(null);
  const [txHash, setTxHash] = useState("");
  const [note, setNote] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["withdrawals", page, statusFilter, networkFilter],
    queryFn: () =>
      getWithdrawals({
        page,
        per_page: 20,
        status: statusFilter !== "all" ? (statusFilter as WithdrawalStatus) : undefined,
        network: networkFilter !== "all" ? (networkFilter as NetworkType) : undefined,
      }),
  });

  const actionMutation = useMutation({
    mutationFn: ({ withdrawalId, action, txHash, note }: { withdrawalId: number; action: "complete" | "reject"; txHash?: string; note?: string }) =>
      withdrawalAction(withdrawalId, { action, tx_hash: txHash, note }),
    onSuccess: (result) => {
      toast({
        title: `Withdrawal ${result.new_status}`,
        description: `Withdrawal #${result.withdrawal_id} has been ${result.new_status}`,
      });
      queryClient.invalidateQueries({ queryKey: ["withdrawals"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      setActionDialog(null);
      setTxHash("");
      setNote("");
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Action failed",
        description: getErrorMessage(error),
      });
    },
  });

  const handleAction = () => {
    if (!actionDialog) return;
    actionMutation.mutate({
      withdrawalId: actionDialog.withdrawal.id,
      action: actionDialog.action,
      txHash: txHash || undefined,
      note: note || undefined,
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: "Copied to clipboard" });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Withdrawals</h1>
      </div>

      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
          </SelectContent>
        </Select>

        <Select value={networkFilter} onValueChange={(v) => { setNetworkFilter(v); setPage(1); }}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by network" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Networks</SelectItem>
            <SelectItem value="BEP-20">BEP-20</SelectItem>
            <SelectItem value="Solana">Solana</SelectItem>
            <SelectItem value="TON">TON</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Fee</TableHead>
              <TableHead>Net</TableHead>
              <TableHead>Network</TableHead>
              <TableHead>Wallet</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[150px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 10 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-16" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.withdrawals.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10} className="text-center py-8 text-muted-foreground">
                  No withdrawals found
                </TableCell>
              </TableRow>
            ) : (
              data?.withdrawals.map((withdrawal) => (
                <TableRow key={withdrawal.id}>
                  <TableCell className="font-mono">#{withdrawal.id}</TableCell>
                  <TableCell>
                    <Link
                      href={`/users/${withdrawal.user_id}`}
                      className="text-primary hover:underline"
                    >
                      {withdrawal.username || `User #${withdrawal.telegram_id}`}
                    </Link>
                  </TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(withdrawal.amount)} XPET
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatCurrency(withdrawal.fee)}
                  </TableCell>
                  <TableCell className="font-medium text-green-600">
                    {formatCurrency(withdrawal.net_amount)}
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${networkColors[withdrawal.network]}`}>
                      {withdrawal.network}
                    </span>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <span className="font-mono text-xs">
                        {truncateAddress(withdrawal.wallet_address)}
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={() => copyToClipboard(withdrawal.wallet_address)}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[withdrawal.status]}>
                      {withdrawal.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(withdrawal.created_at)}
                  </TableCell>
                  <TableCell>
                    {withdrawal.status === "pending" && isAdminOrAbove() ? (
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="success"
                          onClick={() => setActionDialog({ withdrawal, action: "complete" })}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => setActionDialog({ withdrawal, action: "reject" })}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {data && data.total_pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data.page} of {data.total_pages} ({data.total} withdrawals)
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= data.total_pages}
            >
              Next <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      <Dialog open={!!actionDialog} onOpenChange={(open) => !open && setActionDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {actionDialog?.action === "complete" ? "Complete" : "Reject"} Withdrawal
            </DialogTitle>
            <DialogDescription>
              {actionDialog?.action === "complete"
                ? "Mark this withdrawal as completed after sending funds."
                : "This will reject the withdrawal and refund the user's balance."}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Withdrawal ID</p>
                <p className="font-mono">#{actionDialog?.withdrawal.id}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Net Amount</p>
                <p className="font-medium">{formatCurrency(actionDialog?.withdrawal.net_amount ?? 0)} XPET</p>
              </div>
              <div>
                <p className="text-muted-foreground">Network</p>
                <p>{actionDialog?.withdrawal.network}</p>
              </div>
              <div>
                <p className="text-muted-foreground">User</p>
                <p>{actionDialog?.withdrawal.username || `#${actionDialog?.withdrawal.telegram_id}`}</p>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Wallet Address</Label>
              <div className="flex items-center gap-2">
                <code className="flex-1 p-2 bg-muted rounded text-xs break-all">
                  {actionDialog?.withdrawal.wallet_address}
                </code>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => copyToClipboard(actionDialog?.withdrawal.wallet_address ?? "")}
                >
                  <Copy className="h-4 w-4" />
                </Button>
              </div>
            </div>
            {actionDialog?.action === "complete" && (
              <div className="space-y-2">
                <Label htmlFor="txHash">Transaction Hash (optional)</Label>
                <Input
                  id="txHash"
                  placeholder="0x..."
                  value={txHash}
                  onChange={(e) => setTxHash(e.target.value)}
                />
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="note">Note (optional)</Label>
              <Input
                id="note"
                placeholder="Add a note..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActionDialog(null)}>
              Cancel
            </Button>
            <Button
              variant={actionDialog?.action === "complete" ? "success" : "destructive"}
              onClick={handleAction}
              disabled={actionMutation.isPending}
            >
              {actionMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {actionDialog?.action === "complete" ? "Complete" : "Reject"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
