"use client";

import { X } from "lucide-react";
import { useEffect } from "react";

// Right-hand detail drawer (design.md 10.4): closes on Escape, labelled, focus moves into it.
export function DetailDrawer({
  open,
  title,
  onClose,
  children,
}: {
  open: boolean;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <aside
      role="dialog"
      aria-modal="false"
      aria-label={title}
      className="fixed inset-y-0 right-0 z-20 w-full max-w-xl overflow-y-auto border-l border-border-subtle bg-bg p-6"
      style={{ boxShadow: "var(--shadow-card)" }}
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl font-semibold">{title}</h2>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="rounded-control p-1.5 hover:bg-surface"
        >
          <X size={18} aria-hidden />
        </button>
      </div>
      {children}
    </aside>
  );
}
