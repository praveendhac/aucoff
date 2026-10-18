"use client";

import {
  Bug,
  ClipboardCheck,
  FileSearch,
  FileText,
  LayoutDashboard,
  MessageSquareText,
  PanelLeftClose,
  PanelLeftOpen,
  ScrollText,
  Settings,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { NavItem } from "@/lib/nav";

const ICONS = {
  LayoutDashboard,
  ClipboardCheck,
  ShieldCheck,
  Bug,
  FileSearch,
  MessageSquareText,
  FileText,
  ScrollText,
  Settings,
} as const;

export function Sidebar({
  items,
  collapsed,
  onToggle,
}: {
  items: NavItem[];
  collapsed: boolean;
  onToggle: () => void;
}) {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Main"
      className="flex shrink-0 flex-col gap-1 p-3 transition-[width] motion-reduce:transition-none"
      style={{ width: collapsed ? 64 : 232, background: "#0b2a6f", color: "#ffffff" }}
    >
      <div className="mb-3 flex items-center justify-between px-2 pt-1">
        {collapsed ? null : <span className="text-lg font-semibold tracking-tight">AUCoFF</span>}
        <button
          type="button"
          onClick={onToggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="rounded-control p-1.5 hover:bg-white/10"
        >
          {collapsed ? (
            <PanelLeftOpen size={18} aria-hidden />
          ) : (
            <PanelLeftClose size={18} aria-hidden />
          )}
        </button>
      </div>
      {items.map((item) => {
        const Icon = ICONS[item.icon as keyof typeof ICONS];
        const active = item.available && pathname === item.href;
        const content = (
          <>
            <Icon size={18} strokeWidth={1.75} aria-hidden />
            {collapsed ? <span className="sr-only">{item.label}</span> : <span>{item.label}</span>}
            {!item.available && !collapsed ? (
              <span className="ml-auto rounded bg-white/15 px-1.5 text-[10px] uppercase tracking-wide">
                Soon
              </span>
            ) : null}
          </>
        );
        const base = "flex items-center gap-3 rounded-control px-3 py-2 text-sm";
        return item.available ? (
          <Link
            key={item.key}
            href={item.href}
            aria-current={active ? "page" : undefined}
            className={`${base} hover:bg-white/10 ${active ? "bg-white/20 font-medium" : ""}`}
          >
            {content}
          </Link>
        ) : (
          <span
            key={item.key}
            aria-disabled="true"
            className={`${base} cursor-not-allowed opacity-70`}
          >
            {content}
          </span>
        );
      })}
    </nav>
  );
}
