"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Loader2, ExternalLink } from "lucide-react";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  getTasks,
  createTask,
  updateTask,
  deleteTask,
} from "@/lib/api/tasks";
import { formatCurrency } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";
import { Task, CreateTaskRequest, TaskType } from "@/types";

const taskTypeColors: Record<TaskType, string> = {
  TWITTER: "bg-blue-100 text-blue-800",
  TELEGRAM: "bg-cyan-100 text-cyan-800",
  OTHER: "bg-gray-100 text-gray-800",
};

const defaultFormData: CreateTaskRequest = {
  title: "",
  description: "",
  reward_xpet: 0,
  link: "",
  task_type: "OTHER",
  is_active: true,
  order: 0,
};

export default function TasksPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isAdminOrAbove } = useAuthStore();
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<Task | null>(null);
  const [formData, setFormData] = useState<CreateTaskRequest>(defaultFormData);

  const { data, isLoading } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => getTasks(true),
  });

  const createMutation = useMutation({
    mutationFn: createTask,
    onSuccess: () => {
      toast({ title: "Task created" });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setIsCreating(false);
      setFormData(defaultFormData);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CreateTaskRequest> }) =>
      updateTask(id, data),
    onSuccess: () => {
      toast({ title: "Task updated" });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setEditingTask(null);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteTask(id, false),
    onSuccess: () => {
      toast({ title: "Task deleted" });
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      setDeleteDialog(null);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const openEditDialog = (task: Task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description || "",
      reward_xpet: parseFloat(task.reward_xpet),
      link: task.link || "",
      task_type: task.task_type,
      is_active: task.is_active,
      order: task.order,
    });
  };

  const handleSubmit = () => {
    if (editingTask) {
      updateMutation.mutate({ id: editingTask.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const closeDialog = () => {
    setIsCreating(false);
    setEditingTask(null);
    setFormData(defaultFormData);
  };

  const tasks = data?.tasks ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Tasks</h1>
        {isAdminOrAbove() && (
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="h-4 w-4 mr-2" /> Add Task
          </Button>
        )}
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Order</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Reward</TableHead>
              <TableHead>Completions</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-[100px]">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {Array.from({ length: 7 }).map((_, j) => (
                    <TableCell key={j}><Skeleton className="h-4 w-20" /></TableCell>
                  ))}
                </TableRow>
              ))
            ) : tasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No tasks found
                </TableCell>
              </TableRow>
            ) : (
              tasks.map((task) => (
                <TableRow key={task.id} className={!task.is_active ? "opacity-50" : ""}>
                  <TableCell>{task.order}</TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium">{task.title}</span>
                      {task.description && (
                        <span className="text-xs text-muted-foreground truncate max-w-[200px]">
                          {task.description}
                        </span>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${taskTypeColors[task.task_type]}`}>
                      {task.task_type}
                    </span>
                  </TableCell>
                  <TableCell>{formatCurrency(task.reward_xpet)} XPET</TableCell>
                  <TableCell>{task.completions_count}</TableCell>
                  <TableCell>
                    <Badge variant={task.is_active ? "success" : "secondary"}>
                      {task.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      {task.link && (
                        <Button
                          size="icon"
                          variant="ghost"
                          asChild
                        >
                          <a href={task.link} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
                      {isAdminOrAbove() && (
                        <>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => openEditDialog(task)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            size="icon"
                            variant="ghost"
                            onClick={() => setDeleteDialog(task)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isCreating || !!editingTask} onOpenChange={(open) => !open && closeDialog()}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingTask ? "Edit" : "Create"} Task</DialogTitle>
            <DialogDescription>
              {editingTask ? "Update task details" : "Add a new task for users to complete"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Title</Label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Task title"
              />
            </div>
            <div className="space-y-2">
              <Label>Description (optional)</Label>
              <Input
                value={formData.description || ""}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Task description"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Reward (XPET)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.reward_xpet}
                  onChange={(e) => setFormData({ ...formData, reward_xpet: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="space-y-2">
                <Label>Order</Label>
                <Input
                  type="number"
                  value={formData.order}
                  onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <Select
                value={formData.task_type}
                onValueChange={(v) => setFormData({ ...formData, task_type: v as TaskType })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="TWITTER">Twitter</SelectItem>
                  <SelectItem value="TELEGRAM">Telegram</SelectItem>
                  <SelectItem value="OTHER">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Link (optional)</Label>
              <Input
                value={formData.link || ""}
                onChange={(e) => setFormData({ ...formData, link: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
              />
              <Label>Active</Label>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>Cancel</Button>
            <Button
              onClick={handleSubmit}
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {(createMutation.isPending || updateMutation.isPending) && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              {editingTask ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={!!deleteDialog} onOpenChange={(open) => !open && setDeleteDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Task</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{deleteDialog?.title}&quot;? This will deactivate the task.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialog(null)}>Cancel</Button>
            <Button
              variant="destructive"
              onClick={() => deleteDialog && deleteMutation.mutate(deleteDialog.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
