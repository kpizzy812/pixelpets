"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Search, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { getLogs } from "@/lib/api/logs";
import { formatDate } from "@/lib/utils";
import { useAuthStore } from "@/store/auth-store";
import { AdminLog } from "@/types";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

const actionColors: Record<string, string> = {
  "user.balance_adjust": "bg-yellow-100 text-yellow-800",
  "deposit.approve": "bg-green-100 text-green-800",
  "deposit.reject": "bg-red-100 text-red-800",
  "withdrawal.complete": "bg-green-100 text-green-800",
  "withdrawal.reject": "bg-red-100 text-red-800",
  "pet_type.create": "bg-blue-100 text-blue-800",
  "pet_type.update": "bg-blue-100 text-blue-800",
  "pet_type.delete": "bg-red-100 text-red-800",
  "task.create": "bg-blue-100 text-blue-800",
  "task.update": "bg-blue-100 text-blue-800",
  "task.delete": "bg-red-100 text-red-800",
  "config.update": "bg-purple-100 text-purple-800",
  "admin.create": "bg-purple-100 text-purple-800",
  "admin.update": "bg-purple-100 text-purple-800",
};

const actionOptions = [
  { value: "all", label: "All Actions" },
  { value: "user.balance_adjust", label: "Balance Adjust" },
  { value: "deposit.approve", label: "Deposit Approve" },
  { value: "deposit.reject", label: "Deposit Reject" },
  { value: "withdrawal.complete", label: "Withdrawal Complete" },
  { value: "withdrawal.reject", label: "Withdrawal Reject" },
  { value: "pet_type.create", label: "Pet Type Create" },
  { value: "pet_type.update", label: "Pet Type Update" },
  { value: "pet_type.delete", label: "Pet Type Delete" },
  { value: "task.create", label: "Task Create" },
  { value: "task.update", label: "Task Update" },
  { value: "task.delete", label: "Task Delete" },
  { value: "config.update", label: "Config Update" },
];

export default function LogsPage() {
  const router = useRouter();
  const { isSuperAdmin } = useAuthStore();
  const [page, setPage] = useState(1);
  const [actionFilter, setActionFilter] = useState("all");
  const [selectedLog, setSelectedLog] = useState<AdminLog | null>(null);

  // Redirect if not super admin
  useEffect(() => {
    if (!isSuperAdmin()) {
      router.push("/");
    }
  }, [isSuperAdmin, router]);

  const { data, isLoading } = useQuery({
    queryKey: ["logs", page, actionFilter],
    queryFn: () =>
      getLogs({
        page,
        per_page: 50,
        action: actionFilter !== "all" ? actionFilter : undefined,
      }),
    enabled: isSuperAdmin(),
  });

  if (!isSuperAdmin()) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <Shield className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-xl font-semibold">Access Denied</h2>
        <p className="text-muted-foreground">
          Only Super Admins can view audit logs
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Admin Logs</h1>
      </div>

      <div className="flex gap-4">
        <Select
          value={actionFilter}
          onValueChange={(v) => {
            setActionFilter(v);
            setPage(1);
          }}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Filter by action" />
          </SelectTrigger>
          <SelectContent>
            {actionOptions.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Admin</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Target</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>Time</TableHead>
              <TableHead className="w-[80px]">Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 10 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-20" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : data?.logs.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="text-center py-8 text-muted-foreground"
                >
                  No logs found
                </TableCell>
              </TableRow>
            ) : (
              data?.logs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono">#{log.id}</TableCell>
                  <TableCell className="font-medium">
                    {log.admin_username}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        actionColors[log.action] || "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {log.action}
                    </span>
                  </TableCell>
                  <TableCell>
                    {log.target_type && log.target_id ? (
                      <span className="font-mono text-sm">
                        {log.target_type}#{log.target_id}
                      </span>
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </TableCell>
                  <TableCell className="font-mono text-xs">
                    {log.ip_address || "-"}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(log.created_at)}
                  </TableCell>
                  <TableCell>
                    {log.details && Object.keys(log.details).length > 0 ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedLog(log)}
                      >
                        View
                      </Button>
                    ) : (
                      <span className="text-muted-foreground">-</span>
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
            Page {data.page} of {data.total_pages} ({data.total} logs)
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

      {/* Details Dialog */}
      <Dialog open={!!selectedLog} onOpenChange={(open) => !open && setSelectedLog(null)}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Log Details</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Log ID</p>
                <p className="font-mono">#{selectedLog?.id}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Admin</p>
                <p className="font-medium">{selectedLog?.admin_username}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Action</p>
                <p>{selectedLog?.action}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Target</p>
                <p className="font-mono">
                  {selectedLog?.target_type}#{selectedLog?.target_id}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">IP Address</p>
                <p className="font-mono">{selectedLog?.ip_address || "-"}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Time</p>
                <p>{selectedLog && formatDate(selectedLog.created_at)}</p>
              </div>
            </div>
            <div>
              <p className="text-muted-foreground text-sm mb-2">Details</p>
              <pre className="bg-muted p-4 rounded-lg text-xs overflow-auto max-h-64">
                {JSON.stringify(selectedLog?.details, null, 2)}
              </pre>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
