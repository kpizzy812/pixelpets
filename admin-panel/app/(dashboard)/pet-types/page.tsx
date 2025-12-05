"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, Loader2 } from "lucide-react";
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
  getPetTypes,
  createPetType,
  updatePetType,
  deletePetType,
} from "@/lib/api/pet-types";
import { formatCurrency } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";
import { PetType, CreatePetTypeRequest, UpdatePetTypeRequest } from "@/types";

const defaultFormData: CreatePetTypeRequest = {
  name: "",
  emoji: "",
  base_price: 0,
  daily_rate: 0.01,
  roi_cap_multiplier: 1.5,
  level_prices: { BABY: 5, ADULT: 15, MYTHIC: 30 },
  is_active: true,
};

export default function PetTypesPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isAdminOrAbove } = useAuthStore();
  const [editingPetType, setEditingPetType] = useState<PetType | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<PetType | null>(null);
  const [formData, setFormData] = useState<CreatePetTypeRequest>(defaultFormData);

  const { data: petTypes, isLoading } = useQuery({
    queryKey: ["pet-types"],
    queryFn: () => getPetTypes(true),
  });

  const createMutation = useMutation({
    mutationFn: createPetType,
    onSuccess: () => {
      toast({ title: "Pet type created" });
      queryClient.invalidateQueries({ queryKey: ["pet-types"] });
      setIsCreating(false);
      setFormData(defaultFormData);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdatePetTypeRequest }) =>
      updatePetType(id, data),
    onSuccess: () => {
      toast({ title: "Pet type updated" });
      queryClient.invalidateQueries({ queryKey: ["pet-types"] });
      setEditingPetType(null);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deletePetType(id, false),
    onSuccess: () => {
      toast({ title: "Pet type deleted" });
      queryClient.invalidateQueries({ queryKey: ["pet-types"] });
      setDeleteDialog(null);
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const openEditDialog = (petType: PetType) => {
    setEditingPetType(petType);
    setFormData({
      name: petType.name,
      emoji: petType.emoji || "",
      base_price: parseFloat(petType.base_price),
      daily_rate: parseFloat(petType.daily_rate),
      roi_cap_multiplier: parseFloat(petType.roi_cap_multiplier),
      level_prices: petType.level_prices,
      is_active: petType.is_active,
    });
  };

  const handleSubmit = () => {
    if (editingPetType) {
      updateMutation.mutate({ id: editingPetType.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const closeDialog = () => {
    setIsCreating(false);
    setEditingPetType(null);
    setFormData(defaultFormData);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Pet Types</h1>
        {isAdminOrAbove() && (
          <Button onClick={() => setIsCreating(true)}>
            <Plus className="h-4 w-4 mr-2" /> Add Pet Type
          </Button>
        )}
      </div>

      <div className="rounded-md border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Base Price</TableHead>
              <TableHead>Daily Rate</TableHead>
              <TableHead>ROI Cap</TableHead>
              <TableHead>Level Prices</TableHead>
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
            ) : petTypes?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No pet types found
                </TableCell>
              </TableRow>
            ) : (
              petTypes?.map((petType) => (
                <TableRow key={petType.id} className={!petType.is_active ? "opacity-50" : ""}>
                  <TableCell>
                    <span className="font-medium">
                      {petType.emoji} {petType.name}
                    </span>
                  </TableCell>
                  <TableCell>{formatCurrency(petType.base_price)} XPET</TableCell>
                  <TableCell>{(parseFloat(petType.daily_rate) * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(parseFloat(petType.roi_cap_multiplier) * 100).toFixed(0)}%</TableCell>
                  <TableCell className="text-sm">
                    B: {petType.level_prices.BABY} / A: {petType.level_prices.ADULT} / M: {petType.level_prices.MYTHIC}
                  </TableCell>
                  <TableCell>
                    <Badge variant={petType.is_active ? "success" : "secondary"}>
                      {petType.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {isAdminOrAbove() && (
                      <div className="flex gap-1">
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => openEditDialog(petType)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => setDeleteDialog(petType)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Create/Edit Dialog */}
      <Dialog open={isCreating || !!editingPetType} onOpenChange={(open) => !open && closeDialog()}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{editingPetType ? "Edit" : "Create"} Pet Type</DialogTitle>
            <DialogDescription>
              {editingPetType ? "Update pet type details" : "Add a new pet type to the game"}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-4 gap-4">
              <div className="col-span-3 space-y-2">
                <Label>Name</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Pet name"
                />
              </div>
              <div className="space-y-2">
                <Label>Emoji</Label>
                <Input
                  value={formData.emoji || ""}
                  onChange={(e) => setFormData({ ...formData, emoji: e.target.value })}
                  placeholder="🐾"
                />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>Base Price (XPET)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={formData.base_price}
                  onChange={(e) => setFormData({ ...formData, base_price: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="space-y-2">
                <Label>Daily Rate (%)</Label>
                <Input
                  type="number"
                  step="0.1"
                  value={(formData.daily_rate * 100).toFixed(1)}
                  onChange={(e) => setFormData({ ...formData, daily_rate: (parseFloat(e.target.value) || 0) / 100 })}
                />
              </div>
              <div className="space-y-2">
                <Label>ROI Cap (%)</Label>
                <Input
                  type="number"
                  step="1"
                  value={(formData.roi_cap_multiplier * 100).toFixed(0)}
                  onChange={(e) => setFormData({ ...formData, roi_cap_multiplier: (parseFloat(e.target.value) || 0) / 100 })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Level Prices (XPET)</Label>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className="text-xs text-muted-foreground">Baby</Label>
                  <Input
                    type="number"
                    value={formData.level_prices.BABY}
                    onChange={(e) => setFormData({
                      ...formData,
                      level_prices: { ...formData.level_prices, BABY: parseFloat(e.target.value) || 0 },
                    })}
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Adult</Label>
                  <Input
                    type="number"
                    value={formData.level_prices.ADULT}
                    onChange={(e) => setFormData({
                      ...formData,
                      level_prices: { ...formData.level_prices, ADULT: parseFloat(e.target.value) || 0 },
                    })}
                  />
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Mythic</Label>
                  <Input
                    type="number"
                    value={formData.level_prices.MYTHIC}
                    onChange={(e) => setFormData({
                      ...formData,
                      level_prices: { ...formData.level_prices, MYTHIC: parseFloat(e.target.value) || 0 },
                    })}
                  />
                </div>
              </div>
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
              {editingPetType ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Dialog */}
      <Dialog open={!!deleteDialog} onOpenChange={(open) => !open && setDeleteDialog(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Pet Type</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete &quot;{deleteDialog?.name}&quot;? This will deactivate the pet type.
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
