"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import {
  getConfigs,
  getReferralConfig,
  updateReferralConfig,
  updateConfig,
} from "@/lib/api/config";
import { useToast } from "@/hooks/use-toast";
import { getErrorMessage } from "@/lib/api/client";
import { useAuthStore } from "@/store/auth-store";

export default function ConfigPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { isSuperAdmin } = useAuthStore();

  const { data: configs, isLoading: configsLoading } = useQuery({
    queryKey: ["configs"],
    queryFn: getConfigs,
  });

  const { data: referralConfig, isLoading: referralLoading } = useQuery({
    queryKey: ["referral-config"],
    queryFn: getReferralConfig,
  });

  // Referral percentages state
  const [percentages, setPercentages] = useState<Record<string, string>>({});
  const [thresholds, setThresholds] = useState<Record<string, string>>({});

  // Initialize state when data loads
  useState(() => {
    if (referralConfig) {
      setPercentages(Object.fromEntries(
        Object.entries(referralConfig.percentages).map(([k, v]) => [k, v.toString()])
      ));
      setThresholds(Object.fromEntries(
        Object.entries(referralConfig.unlock_thresholds).map(([k, v]) => [k, v.toString()])
      ));
    }
  });

  // Config values state
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  const updateRefMutation = useMutation({
    mutationFn: updateReferralConfig,
    onSuccess: () => {
      toast({ title: "Referral config updated" });
      queryClient.invalidateQueries({ queryKey: ["referral-config"] });
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const updateConfigMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: unknown }) =>
      updateConfig(key, { value }),
    onSuccess: () => {
      toast({ title: "Config updated" });
      queryClient.invalidateQueries({ queryKey: ["configs"] });
    },
    onError: (error) => {
      toast({ variant: "destructive", title: "Failed", description: getErrorMessage(error) });
    },
  });

  const handleSaveReferral = () => {
    const newPercentages = Object.fromEntries(
      Object.entries(percentages).map(([k, v]) => [k, parseInt(v) || 0])
    );
    const newThresholds = Object.fromEntries(
      Object.entries(thresholds).map(([k, v]) => [k, parseInt(v) || 0])
    );
    updateRefMutation.mutate({
      percentages: newPercentages,
      unlock_thresholds: newThresholds,
    });
  };

  const handleSaveConfig = (key: string) => {
    const value = configValues[key];
    if (value === undefined) return;

    // Try to parse as number or JSON
    let parsedValue: unknown = value;
    if (!isNaN(Number(value))) {
      parsedValue = Number(value);
    } else {
      try {
        parsedValue = JSON.parse(value);
      } catch {
        // Keep as string
      }
    }

    updateConfigMutation.mutate({ key, value: parsedValue });
  };

  const getConfigValue = (key: string): string => {
    if (configValues[key] !== undefined) return configValues[key];
    const config = configs?.find((c) => c.key === key);
    if (!config) return "";
    return typeof config.value === "object"
      ? JSON.stringify(config.value)
      : String(config.value);
  };

  const isLoading = configsLoading || referralLoading;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Configuration</h1>
        <div className="grid gap-6 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-64" />
          ))}
        </div>
      </div>
    );
  }

  // Initialize percentages and thresholds from data
  const currentPercentages = Object.keys(percentages).length > 0
    ? percentages
    : Object.fromEntries(
        Object.entries(referralConfig?.percentages ?? {}).map(([k, v]) => [k, v.toString()])
      );
  const currentThresholds = Object.keys(thresholds).length > 0
    ? thresholds
    : Object.fromEntries(
        Object.entries(referralConfig?.unlock_thresholds ?? {}).map(([k, v]) => [k, v.toString()])
      );

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Configuration</h1>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Referral Config */}
        <Card>
          <CardHeader>
            <CardTitle>Referral System</CardTitle>
            <CardDescription>Configure referral percentages and unlock thresholds</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label className="text-base font-medium">Reward Percentages (%)</Label>
              <p className="text-sm text-muted-foreground mb-4">
                Percentage of referral&apos;s claim that goes to each level
              </p>
              <div className="grid grid-cols-5 gap-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div key={level}>
                    <Label className="text-xs">Level {level}</Label>
                    <Input
                      type="number"
                      value={currentPercentages[level.toString()] || ""}
                      onChange={(e) =>
                        setPercentages({ ...currentPercentages, [level.toString()]: e.target.value })
                      }
                      disabled={!isSuperAdmin()}
                    />
                  </div>
                ))}
              </div>
            </div>
            <Separator />
            <div>
              <Label className="text-base font-medium">Unlock Thresholds</Label>
              <p className="text-sm text-muted-foreground mb-4">
                Number of active referrals needed to unlock each level
              </p>
              <div className="grid grid-cols-5 gap-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div key={level}>
                    <Label className="text-xs">Level {level}</Label>
                    <Input
                      type="number"
                      value={currentThresholds[level.toString()] || ""}
                      onChange={(e) =>
                        setThresholds({ ...currentThresholds, [level.toString()]: e.target.value })
                      }
                      disabled={!isSuperAdmin()}
                    />
                  </div>
                ))}
              </div>
            </div>
            {isSuperAdmin() && (
              <Button
                onClick={handleSaveReferral}
                disabled={updateRefMutation.isPending}
                className="w-full"
              >
                {updateRefMutation.isPending ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Save className="mr-2 h-4 w-4" />
                )}
                Save Referral Config
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Withdrawal Config */}
        <Card>
          <CardHeader>
            <CardTitle>Withdrawal Settings</CardTitle>
            <CardDescription>Configure withdrawal fees and limits</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Minimum Withdrawal (XPET)</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  step="0.01"
                  value={getConfigValue("withdraw_min")}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, withdraw_min: e.target.value })
                  }
                  disabled={!isSuperAdmin()}
                />
                {isSuperAdmin() && (
                  <Button
                    size="icon"
                    onClick={() => handleSaveConfig("withdraw_min")}
                    disabled={updateConfigMutation.isPending}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Fixed Fee (XPET)</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  step="0.01"
                  value={getConfigValue("withdraw_fee_fixed")}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, withdraw_fee_fixed: e.target.value })
                  }
                  disabled={!isSuperAdmin()}
                />
                {isSuperAdmin() && (
                  <Button
                    size="icon"
                    onClick={() => handleSaveConfig("withdraw_fee_fixed")}
                    disabled={updateConfigMutation.isPending}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
            <div className="space-y-2">
              <Label>Percentage Fee (%)</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  step="0.1"
                  value={getConfigValue("withdraw_fee_percent")}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, withdraw_fee_percent: e.target.value })
                  }
                  disabled={!isSuperAdmin()}
                />
                {isSuperAdmin() && (
                  <Button
                    size="icon"
                    onClick={() => handleSaveConfig("withdraw_fee_percent")}
                    disabled={updateConfigMutation.isPending}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Game Config */}
        <Card>
          <CardHeader>
            <CardTitle>Game Settings</CardTitle>
            <CardDescription>Configure game parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Pet Slots Limit</Label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={getConfigValue("pet_slots_limit")}
                  onChange={(e) =>
                    setConfigValues({ ...configValues, pet_slots_limit: e.target.value })
                  }
                  disabled={!isSuperAdmin()}
                />
                {isSuperAdmin() && (
                  <Button
                    size="icon"
                    onClick={() => handleSaveConfig("pet_slots_limit")}
                    disabled={updateConfigMutation.isPending}
                  >
                    <Save className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Deposit Addresses */}
        <Card>
          <CardHeader>
            <CardTitle>Deposit Addresses</CardTitle>
            <CardDescription>Wallet addresses for each network</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {["BEP-20", "Solana", "TON"].map((network) => {
              const addresses = configs?.find((c) => c.key === "deposit_addresses")?.value as
                | Record<string, string>
                | undefined;
              return (
                <div key={network} className="space-y-2">
                  <Label>{network}</Label>
                  <Input
                    value={addresses?.[network] || "Not configured"}
                    disabled
                    className="font-mono text-xs"
                  />
                </div>
              );
            })}
            <p className="text-xs text-muted-foreground">
              Contact developer to update deposit addresses
            </p>
          </CardContent>
        </Card>
      </div>

      {/* All Configs Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Configuration Values</CardTitle>
          <CardDescription>Complete list of system configuration</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {configs?.map((config) => (
              <div
                key={config.key}
                className="flex items-center justify-between py-2 border-b last:border-0"
              >
                <div>
                  <p className="font-medium">{config.key}</p>
                  {config.description && (
                    <p className="text-xs text-muted-foreground">{config.description}</p>
                  )}
                </div>
                <code className="text-sm bg-muted px-2 py-1 rounded max-w-[300px] truncate">
                  {typeof config.value === "object"
                    ? JSON.stringify(config.value)
                    : String(config.value)}
                </code>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
