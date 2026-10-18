// Design tokens (specs/design.md section 10.2). This file is the single source: globals.css repeats
// the same hex values (a test keeps the two in sync) and the contrast test checks every pair here.
export type Theme = "light" | "dark";

export const surfaces = {
  light: {
    bg: "#FFFFFF",
    surface: "#F8FAFC",
    "border-subtle": "#E2E8F0",
    "border-control": "#64748B",
    text: "#0F172A",
    "text-muted": "#475569",
  },
  dark: {
    bg: "#0B1220",
    surface: "#111A2E",
    "border-subtle": "#1E293B",
    "border-control": "#64748B",
    text: "#E5E7EB",
    "text-muted": "#9CA3AF",
  },
} as const;

export const brand = {
  light: { deep: "#0B2A6F", brand: "#1D4ED8", teal: "#0F766E", onBrand: "#FFFFFF" },
  dark: { deep: "#93C5FD", brand: "#60A5FA", teal: "#2DD4BF", onBrand: "#0B1220" },
} as const;

export type StatusKey = "pass" | "partial" | "fail" | "unknown" | "na" | "pending";

// foreground (text/icon) and tint (badge fill) per status and theme
export const status: Record<Theme, Record<StatusKey, { fg: string; tint: string }>> = {
  light: {
    pass: { fg: "#15803D", tint: "#DCFCE7" },
    partial: { fg: "#B45309", tint: "#FEF3C7" },
    fail: { fg: "#B91C1C", tint: "#FEE2E2" },
    unknown: { fg: "#4B5563", tint: "#F3F4F6" },
    na: { fg: "#475569", tint: "#F1F5F9" },
    pending: { fg: "#1D4ED8", tint: "#DBEAFE" },
  },
  dark: {
    pass: { fg: "#4ADE80", tint: "#052E16" },
    partial: { fg: "#FBBF24", tint: "#422006" },
    fail: { fg: "#F87171", tint: "#450A0A" },
    unknown: { fg: "#9CA3AF", tint: "#1F2937" },
    na: { fg: "#94A3B8", tint: "#1E293B" },
    pending: { fg: "#60A5FA", tint: "#172554" },
  },
};

export type SeverityKey = "critical" | "high" | "medium" | "low" | "info";

export const severity: Record<Theme, Record<SeverityKey, string>> = {
  light: {
    critical: "#B91C1C",
    high: "#C2410C",
    medium: "#A16207",
    low: "#0369A1",
    info: "#4B5563",
  },
  dark: {
    critical: "#F87171",
    high: "#FB923C",
    medium: "#FACC15",
    low: "#38BDF8",
    info: "#9CA3AF",
  },
};
