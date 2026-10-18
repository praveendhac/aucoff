import type { PostureDashboard } from "@/lib/dashboard";
import { Delta } from "./delta";

const CARDS: {
  key: keyof PostureDashboard["kpis"];
  label: string;
  unit: string;
  lowerIsBetter: boolean;
  hero?: boolean;
}[] = [
  { key: "posture_score", label: "Posture score", unit: "", lowerIsBetter: false, hero: true },
  { key: "coverage_pct", label: "Control coverage", unit: "%", lowerIsBetter: false, hero: true },
  { key: "open_findings", label: "Open findings", unit: "", lowerIsBetter: true },
  { key: "pending_approvals", label: "Pending approvals", unit: "", lowerIsBetter: true },
  { key: "evidence_freshness_pct", label: "Evidence freshness", unit: "%", lowerIsBetter: false },
];

export function KpiStrip({ kpis }: { kpis: PostureDashboard["kpis"] }) {
  return (
    <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-5" aria-label="Key figures">
      {CARDS.map((c) => {
        const kpi = kpis[c.key];
        return (
          <li
            key={c.key}
            className={`lift rounded-card p-5 ${c.hero ? "hero-card" : "border border-border-subtle bg-surface"}`}
            style={c.hero ? undefined : { boxShadow: "var(--shadow-card)" }}
          >
            <p className={`text-sm ${c.hero ? "" : "text-muted"}`}>{c.label}</p>
            <p className="tabular mt-1 text-4xl font-bold tracking-tight">
              {kpi.value}
              {c.unit}
            </p>
            <div className="mt-2">
              <Delta
                value={kpi.delta_vs_previous}
                lowerIsBetter={c.lowerIsBetter}
                unit={c.unit}
                onDark={c.hero}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}
