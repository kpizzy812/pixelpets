"use client";

import { useRouter } from "next/navigation";
import { LogOut, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { useAuthStore } from "@/store/auth-store";

const roleLabels = {
  super_admin: "Super Admin",
  admin: "Admin",
  moderator: "Moderator",
};

const roleVariants = {
  super_admin: "destructive" as const,
  admin: "default" as const,
  moderator: "secondary" as const,
};

export function Header() {
  const router = useRouter();
  const { admin, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const initials = admin?.username
    ? admin.username.slice(0, 2).toUpperCase()
    : "AD";

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-lg font-semibold">Admin Panel</h1>
      </div>

      <div className="flex items-center gap-4">
        {admin && (
          <Badge variant={roleVariants[admin.role]}>
            {roleLabels[admin.role]}
          </Badge>
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-8 w-8 rounded-full">
              <Avatar className="h-8 w-8">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end" forceMount>
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {admin?.username}
                </p>
                {admin?.email && (
                  <p className="text-xs leading-none text-muted-foreground">
                    {admin.email}
                  </p>
                )}
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              <span>Log out</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
