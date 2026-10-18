import {
  ChevronDown,
  ChevronUp,
  ChevronsUp,
  CircleCheck,
  CircleHelp,
  CircleMinus,
  CircleX,
  Clock,
  Info,
  Minus,
  TriangleAlert,
} from "lucide-react";
import type { StatusKey, SeverityKey } from "@/lib/tokens";

// Colour never carries meaning alone: every status and severity has an icon and a text label
// (design.md section 10.2 usage rules).
const STATUS: Record<StatusKey, { label: string; Icon: typeof CircleCheck }> = {
  pass: { label: "Pass", Icon: CircleCheck },
  partial: { label: "Partial", Icon: TriangleAlert },
  fail: { label: "Fail", Icon: CircleX },
  unknown: { label: "Unknown", Icon: CircleHelp },
  na: { label: "Not applicable", Icon: CircleMinus },
  pending: { label: "Awaiting approval", Icon: Clock },
};

export function StatusBadge({ status }: { status: StatusKey }) {
  const { label, Icon } = STATUS[status];
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium"
      style={{ color: `var(--${status})`, background: `var(--${status}-tint)` }}
    >
      <Icon size={14} strokeWidth={1.75} aria-hidden />
      {label}
    </span>
  );
}

const SEVERITY: Record<SeverityKey, { label: string; Icon: typeof Info }> = {
  critical: { label: "Critical", Icon: ChevronsUp },
  high: { label: "High", Icon: ChevronUp },
  medium: { label: "Medium", Icon: Minus },
  low: { label: "Low", Icon: ChevronDown },
  info: { label: "Info", Icon: Info },
};

export function SeverityLabel({ severity }: { severity: SeverityKey }) {
  const { label, Icon } = SEVERITY[severity];
  return (
    <span
      className="inline-flex items-center gap-1.5 text-sm font-medium"
      style={{ color: `var(--sev-${severity})` }}
    >
      <Icon size={16} strokeWidth={1.75} aria-hidden />
      {label}
    </span>
  );
}
