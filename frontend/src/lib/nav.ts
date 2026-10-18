// Sidebar items and who sees them (design.md section 10.4). Hiding an item is a convenience only;
// the API enforces access with scopes (ZT-1, SEC-1).
export type Role = "compliance_officer" | "auditor" | "engineer" | "executive" | "ciso" | "admin";

export interface NavItem {
  key: string;
  label: string;
  href: string;
  icon: string; // lucide icon name, resolved in the sidebar
  roles: Role[] | "all";
  available: boolean; // false = not built yet, shown disabled
}

const ALL_CONTENT: Role[] = ["compliance_officer", "ciso"];

export const NAV: NavItem[] = [
  {
    key: "dashboard",
    label: "Dashboard",
    href: "/",
    icon: "LayoutDashboard",
    roles: "all",
    available: true,
  },
  {
    key: "assessments",
    label: "Assessments",
    href: "/assessments",
    icon: "ClipboardCheck",
    roles: [...ALL_CONTENT, "engineer"],
    available: false,
  },
  {
    key: "controls",
    label: "Controls",
    href: "/controls",
    icon: "ShieldCheck",
    roles: [...ALL_CONTENT, "engineer", "auditor"],
    available: true,
  },
  {
    key: "findings",
    label: "Findings",
    href: "/findings",
    icon: "Bug",
    roles: [...ALL_CONTENT, "engineer"],
    available: true,
  },
  {
    key: "evidence",
    label: "Evidence",
    href: "/evidence",
    icon: "FileSearch",
    roles: [...ALL_CONTENT, "engineer", "auditor"],
    available: true,
  },
  {
    key: "questionnaires",
    label: "Questionnaires",
    href: "/questionnaires",
    icon: "MessageSquareText",
    roles: [...ALL_CONTENT, "engineer"],
    available: false,
  },
  {
    key: "reports",
    label: "Reports",
    href: "/reports",
    icon: "FileText",
    roles: [...ALL_CONTENT, "auditor", "executive"],
    available: false,
  },
  {
    key: "audit",
    label: "Audit log",
    href: "/audit-log",
    icon: "ScrollText",
    roles: ["ciso", "auditor", "admin"],
    available: false,
  },
  {
    key: "settings",
    label: "Settings",
    href: "/settings",
    icon: "Settings",
    roles: ["admin"],
    available: false,
  },
];

export function navFor(roles: readonly string[]): NavItem[] {
  return NAV.filter((item) => item.roles === "all" || item.roles.some((r) => roles.includes(r)));
}
