"use client";

import { SeverityLabel } from "@/components/status";
import { type Column } from "@/components/table/data-table";
import { ListView } from "@/components/table/list-view";

export interface Finding {
  id: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "in_progress" | "accepted_risk" | "resolved";
  framework_id: string;
  control_id: string;
  first_seen: string;
  age_days: number;
}

const RANK = { critical: 0, high: 1, medium: 2, low: 3 } as const;
export const STATUS_LABEL: Record<Finding["status"], string> = {
  open: "Open",
  in_progress: "In progress",
  accepted_risk: "Accepted risk",
  resolved: "Resolved",
};

const columns: Column<Finding>[] = [
  {
    key: "id",
    header: "ID",
    render: (f) => <span className="font-mono">{f.id}</span>,
    sortValue: (f) => f.id,
  },
  { key: "title", header: "Finding", render: (f) => f.title, sortValue: (f) => f.title },
  {
    key: "severity",
    header: "Severity",
    render: (f) => <SeverityLabel severity={f.severity} />,
    sortValue: (f) => RANK[f.severity],
  },
  {
    key: "status",
    header: "Status",
    render: (f) => STATUS_LABEL[f.status],
    sortValue: (f) => f.status,
  },
  {
    key: "framework",
    header: "Framework",
    render: (f) => f.framework_id,
    sortValue: (f) => f.framework_id,
  },
  {
    key: "age",
    header: "Age (days)",
    render: (f) => <span className="tabular">{f.age_days}</span>,
    sortValue: (f) => f.age_days,
  },
];

export function FindingsView() {
  return (
    <ListView<Finding>
      path="/findings"
      caption="Findings"
      columns={columns}
      rowKey={(f) => f.id}
      emptyMessage="No findings match these filters."
      filters={[
        {
          name: "severity",
          label: "Severity",
          options: ["critical", "high", "medium", "low"].map((v) => ({
            value: v,
            label: v[0].toUpperCase() + v.slice(1),
          })),
        },
        {
          name: "status",
          label: "Status",
          options: Object.entries(STATUS_LABEL).map(([value, label]) => ({ value, label })),
        },
      ]}
      detailTitle={(f) => f.id}
      renderDetail={(f) => (
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="text-muted">Finding</dt>
            <dd className="font-medium">{f.title}</dd>
          </div>
          <div>
            <dt className="text-muted">Severity</dt>
            <dd>
              <SeverityLabel severity={f.severity} />
            </dd>
          </div>
          <div>
            <dt className="text-muted">Status</dt>
            <dd>{STATUS_LABEL[f.status]}</dd>
          </div>
          <div>
            <dt className="text-muted">Framework</dt>
            <dd>{f.framework_id}</dd>
          </div>
          <div>
            <dt className="text-muted">Control</dt>
            <dd className="font-mono">{f.control_id}</dd>
          </div>
          <div>
            <dt className="text-muted">First seen</dt>
            <dd>
              {f.first_seen} ({f.age_days} days ago)
            </dd>
          </div>
        </dl>
      )}
    />
  );
}
