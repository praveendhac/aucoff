"use client";

import { SeverityLabel } from "@/components/status";
import { type Column } from "@/components/table/data-table";
import { ListView } from "@/components/table/list-view";

export interface UnifiedControl {
  id: string;
  title: string;
  description: string;
  domain: string;
  severity: "critical" | "high" | "medium" | "low";
  check_type: "automated" | "manual" | "hybrid";
  status: "draft" | "approved";
  requirements: { framework: string; ref: string }[];
}

const RANK = { critical: 0, high: 1, medium: 2, low: 3 } as const;

const columns: Column<UnifiedControl>[] = [
  {
    key: "id",
    header: "ID",
    render: (c) => <span className="font-mono">{c.id}</span>,
    sortValue: (c) => c.id,
  },
  { key: "title", header: "Control", render: (c) => c.title, sortValue: (c) => c.title },
  { key: "domain", header: "Domain", render: (c) => c.domain, sortValue: (c) => c.domain },
  {
    key: "severity",
    header: "Severity",
    render: (c) => <SeverityLabel severity={c.severity} />,
    sortValue: (c) => RANK[c.severity],
  },
  { key: "check", header: "Check", render: (c) => c.check_type, sortValue: (c) => c.check_type },
  {
    key: "status",
    header: "Review",
    render: (c) => (c.status === "approved" ? "Approved" : "Draft"),
    sortValue: (c) => c.status,
  },
];

export function ControlsView() {
  return (
    <ListView<UnifiedControl>
      path="/unified-controls"
      caption="Unified controls"
      columns={columns}
      rowKey={(c) => c.id}
      emptyMessage="The control catalogue is empty. Controls are authored as YAML files in data/controls (see its README)."
      filters={[
        {
          name: "framework",
          label: "Framework",
          options: [
            { value: "soc2-2017", label: "SOC 2" },
            { value: "pci-dss-4.0.1", label: "PCI DSS v4.0.1" },
            { value: "rbi-pso-md-2024", label: "RBI PSO Master Directions 2024" },
            { value: "rbi-afa-draft", label: "RBI authentication framework (draft)" },
            { value: "rbi-dpsc-2026", label: "RBI DPSC 2026 (banks)" },
            { value: "iso27001-2022", label: "ISO/IEC 27001:2022" },
          ],
        },
      ]}
      detailTitle={(c) => c.id}
      renderDetail={(c) => (
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="text-muted">Control</dt>
            <dd className="font-medium">{c.title}</dd>
          </div>
          <div>
            <dt className="text-muted">Description</dt>
            <dd>{c.description}</dd>
          </div>
          <div>
            <dt className="text-muted">Severity</dt>
            <dd>
              <SeverityLabel severity={c.severity} />
            </dd>
          </div>
          <div>
            <dt className="text-muted">Requirements (clause identifiers)</dt>
            <dd>
              <ul className="list-disc pl-5">
                {c.requirements.map((r) => (
                  <li key={`${r.framework}-${r.ref}`}>
                    {r.framework} <span className="font-mono">{r.ref}</span>
                  </li>
                ))}
              </ul>
            </dd>
          </div>
        </dl>
      )}
    />
  );
}
