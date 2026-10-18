"use client";

import { LogOut, Search } from "lucide-react";
import { signOut } from "next-auth/react";
import { useState } from "react";
import { navFor } from "@/lib/nav";
import { Sidebar } from "./sidebar";
import { ThemeToggle } from "./theme";

export function AppShell({
  roles,
  tenantId,
  children,
}: {
  roles: string[];
  tenantId?: string;
  children: React.ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className="flex min-h-screen">
      <Sidebar
        items={navFor(roles)}
        collapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-3 border-b border-border-subtle bg-bg px-4 py-2">
          <span
            className="rounded-control bg-surface px-3 py-1 text-xs text-muted"
            title="Current tenant"
          >
            Tenant <span className="font-mono">{tenantId ? tenantId.slice(0, 8) : "unknown"}</span>
          </span>
          <div className="mx-auto flex w-full max-w-xl items-center gap-2 rounded-control border border-border-control px-3 py-1.5 text-muted">
            <Search size={16} aria-hidden />
            <input
              type="search"
              disabled
              aria-label="Search (coming soon)"
              placeholder="Search coming soon"
              className="w-full bg-transparent text-sm outline-none"
            />
          </div>
          <ThemeToggle />
          <button
            type="button"
            onClick={() => signOut({ callbackUrl: "/login" })}
            className="flex items-center gap-2 rounded-control px-3 py-1.5 text-sm text-muted hover:bg-surface"
          >
            <LogOut size={16} aria-hidden /> Sign out
          </button>
        </header>
        <main className="mx-auto w-full max-w-[1440px] flex-1 p-6">{children}</main>
      </div>
    </div>
  );
}
