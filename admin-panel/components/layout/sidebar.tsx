"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  ArrowDownToLine,
  ArrowUpFromLine,
  PawPrint,
  ListTodo,
  Settings,
  ScrollText,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/store/auth-store";
import { useState } from "react";

const navItems = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Users",
    href: "/users",
    icon: Users,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Deposits",
    href: "/deposits",
    icon: ArrowDownToLine,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Withdrawals",
    href: "/withdrawals",
    icon: ArrowUpFromLine,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Pet Types",
    href: "/pet-types",
    icon: PawPrint,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Tasks",
    href: "/tasks",
    icon: ListTodo,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Config",
    href: "/config",
    icon: Settings,
    roles: ["super_admin", "admin", "moderator"],
  },
  {
    title: "Logs",
    href: "/logs",
    icon: ScrollText,
    roles: ["super_admin"],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { admin } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const filteredNavItems = navItems.filter(
    (item) => admin && item.roles.includes(admin.role)
  );

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-card transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-14 items-center border-b px-4">
        {!collapsed && (
          <Link href="/" className="flex items-center gap-2 font-semibold">
            <PawPrint className="h-6 w-6" />
            <span>Pixel Pets Admin</span>
          </Link>
        )}
        {collapsed && (
          <Link href="/" className="mx-auto">
            <PawPrint className="h-6 w-6" />
          </Link>
        )}
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {filteredNavItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.title : undefined}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.title}</span>}
            </Link>
          );
        })}
      </nav>

      <div className="border-t p-2">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-center"
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>
    </aside>
  );
}
