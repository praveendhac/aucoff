import type { PostureDashboard } from "@/lib/dashboard";
import type { SeverityKey, StatusKey } from "@/lib/tokens";
import { Delta } from "./delta";
import { SeverityLabel, StatusBadge } from "../status";

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section
      className="rounded-card border border-border-subtle bg-surface p-5"
      style={{ boxShadow: "var(--shadow-card)" }}
    >
      <h2 className="mb-4 text-base font-semibold">{title}</h2>
      {children}
    </section>
  );
}

const ORDER: { key: keyof PostureDashboard["status_distribution"]; status: StatusKey }[] = [
  { key: "pass", status: "pass" },
  { key: "partial", status: "partial" },
  { key: "fail", status: "fail" },
  { key: "unknown", status: "unknown" },
  { key: "not_applicable", status: "na" },
];

export function StatusDistribution({ data }: { data: PostureDashboard["status_distribution"] }) {
  const total = ORDER.reduce((n, o) => n + data[o.key], 0);
  return (
    <Card title="Control status">
      <div
        role="img"
        aria-label={`Control status: ${ORDER.map((o) => `${data[o.key]} ${o.status}`).join(", ")}`}
        className="mb-4 flex h-3 overflow-hidden rounded-full"
      >
        {ORDER.map((o) => (
          <div
            key={o.key}
            style={{ width: `${(data[o.key] / total) * 100}%`, background: `var(--${o.status})` }}
          />
        ))}
      </div>
      <ul className="space-y-2">
        {ORDER.map((o) => (
          <li key={o.key} className="flex items-center justify-between">
            <StatusBadge status={o.status} />
            <span className="tabular text-sm">
              {data[o.key]}{" "}
              <span className="text-muted">({Math.round((data[o.key] / total) * 100)}%)</span>
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

export function SeverityComparison({ rows }: { rows: PostureDashboard["severity_comparison"] }) {
  const max = Math.max(...rows.flatMap((r) => [r.latest, r.previous, r.before_previous]), 1);
  return (
    <Card title="Failing controls by severity: latest scan vs the two before">
      <table className="w-full text-sm">
        <caption className="sr-only">
          Failing controls by severity for the latest and the two previous scans
        </caption>
        <thead>
          <tr className="text-left text-xs text-muted">
            <th scope="col" className="pb-2 font-medium">
              Severity
            </th>
            <th scope="col" className="pb-2 font-medium">
              Latest
            </th>
            <th scope="col" className="pb-2 font-medium">
              Previous
            </th>
            <th scope="col" className="pb-2 font-medium">
              Two before
            </th>
            <th scope="col" className="pb-2 font-medium">
              Change
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.severity} className="border-t border-border-subtle">
              <th scope="row" className="py-2 text-left font-normal">
                <SeverityLabel severity={r.severity as SeverityKey} />
              </th>
              <td className="tabular py-2">
                <span className="flex items-center gap-2">
                  {r.latest}
                  <span
                    aria-hidden
                    className="inline-block h-2 rounded"
                    style={{
                      width: `${(r.latest / max) * 60}px`,
                      background: `var(--sev-${r.severity})`,
                    }}
                  />
                </span>
              </td>
              <td className="tabular py-2">{r.previous}</td>
              <td className="tabular py-2">{r.before_previous}</td>
              <td className="py-2">
                <Delta value={r.latest - r.previous} lowerIsBetter />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

export function FrameworkCoverage({ rows }: { rows: PostureDashboard["frameworks"] }) {
  return (
    <Card title="Coverage by framework">
      <ul className="space-y-4">
        {rows.map((f) => (
          <li key={f.framework_id}>
            <div className="mb-1 flex items-baseline justify-between gap-2">
              <span className="text-sm font-medium">{f.name}</span>
              <span className="tabular text-sm font-semibold">{f.coverage_pct}%</span>
            </div>
            <div
              role="progressbar"
              aria-label={`${f.name} coverage`}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={f.coverage_pct}
              className="h-2 overflow-hidden rounded-full"
              style={{ background: "var(--border-subtle)" }}
            >
              <div
                className="h-full rounded-full"
                style={{ width: `${f.coverage_pct}%`, background: "var(--brand)" }}
              />
            </div>
            <div className="mt-1">
              <Delta value={f.delta_vs_previous} unit=" pts" />
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
