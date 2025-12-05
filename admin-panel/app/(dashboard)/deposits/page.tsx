"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ChevronLeft,
  ChevronRight,
  Check,
  X,
  Loader2,
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
import { getDeposits, depositAction } from "@/lib/api/deposits";
import { formatCurrency, formatDate } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";
import { Deposit, DepositStatus, NetworkType } from "@/types";
import Link from "next/link";

const statusColors: Record<DepositStatus, "default" | "success" | "destructive"> = {
  pending: "default",
  approved: "success",
  rejected: "destructive",
};

const networkColors: Record<NetworkType, string> = {
  "BEP-20": "bg-yellow-100 text-yellow-800",
  "Solana": "bg-purple-100 text-purple-800",
  "TON": "bg-blue-100 text-blue-800",
};

export default function DepositsPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isAdminOrAbove } = useAuthStore();
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [networkFilter, setNetworkFilter] = useState<string>("all");
  const [actionDialog, setActionDialog] = useState<{
    deposit: Deposit;
    action: "approve" | "reject";
  } | null>(null);
  const [note, setNote] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["deposits", page, statusFilter, networkFilter],
    queryFn: () =>
      getDeposits({
        page,
        per_page: 20,
        status: statusFilter !== "all" ? (statusFilter as DepositStatus) : undefined,
        network: networkFilter !== "all" ? (networkFilter as NetworkType) : undefined,
      }),
  });

  const actionMutation = useMutation({
    mutationFn: ({ depositId, action, note }: { depositId: number; action: "approve" | "reject"; note?: string }) =>
      depositAction(depositId, { action, note }),
    onSuccess: (result) => {
      toast({
        title: `Deposit ${result.new_status}`,
        description: `Deposit #${result.deposit_id} has been ${result.new_status}`,
      });
      queryClient.invalidateQueries({ queryKey: ["deposits"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      setActionDialog(null);
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
      depositId: actionDialog.deposit.id,
      action: actionDialog.action,
      note: note || undefined,
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Deposits</h1>
      </div>

      <div className="flex gap-4">
        <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
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
              <TableHead>Network</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="w-[150px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.deposits.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No deposits found
                </TableCell>
              </TableRow>
            ) : (
              data?.deposits.map((deposit) => (
                <TableRow key={deposit.id}>
                  <TableCell className="font-mono">#{deposit.id}</TableCell>
                  <TableCell>
                    <Link
                      href={`/users/${deposit.user_id}`}
                      className="text-primary hover:underline"
                    >
                      {deposit.username || `User #${deposit.telegram_id}`}
                    </Link>
                  </TableCell>
                  <TableCell className="font-medium">
                    {formatCurrency(deposit.amount)} XPET
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${networkColors[deposit.network]}`}>
                      {deposit.network}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusColors[deposit.status]}>
                      {deposit.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(deposit.created_at)}
                  </TableCell>
                  <TableCell>
                    {deposit.status === "pending" && isAdminOrAbove() ? (
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="success"
                          onClick={() => setActionDialog({ deposit, action: "approve" })}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => setActionDialog({ deposit, action: "reject" })}
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
            Page {data.page} of {data.total_pages} ({data.total} deposits)
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
              {actionDialog?.action === "approve" ? "Approve" : "Reject"} Deposit
            </DialogTitle>
            <DialogDescription>
              {actionDialog?.action === "approve"
                ? `This will credit ${formatCurrency(actionDialog?.deposit.amount ?? 0)} XPET to the user's balance.`
                : "This will reject the deposit request."}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Deposit ID</p>
                <p className="font-mono">#{actionDialog?.deposit.id}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Amount</p>
                <p className="font-medium">{formatCurrency(actionDialog?.deposit.amount ?? 0)} XPET</p>
              </div>
              <div>
                <p className="text-muted-foreground">Network</p>
                <p>{actionDialog?.deposit.network}</p>
              </div>
              <div>
                <p className="text-muted-foreground">User</p>
                <p>{actionDialog?.deposit.username || `#${actionDialog?.deposit.telegram_id}`}</p>
              </div>
            </div>
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
              variant={actionDialog?.action === "approve" ? "success" : "destructive"}
              onClick={handleAction}
              disabled={actionMutation.isPending}
            >
              {actionMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {actionDialog?.action === "approve" ? "Approve" : "Reject"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
