"use client";

import { CircleCheck, Clock } from "lucide-react";
import { type Column } from "@/components/table/data-table";
import { ListView } from "@/components/table/list-view";

export interface EvidenceItem {
  id: string;
  title: string;
  source: "aws" | "kubernetes" | "github" | "entra" | "upload";
  collected_at: string;
  fresh: boolean;
}

const SOURCE_LABEL: Record<EvidenceItem["source"], string> = {
  aws: "AWS",
  kubernetes: "Kubernetes",
  github: "GitHub",
  entra: "Entra ID",
  upload: "Uploaded document",
};

function Freshness({ fresh }: { fresh: boolean }) {
  const Icon = fresh ? CircleCheck : Clock;
  return (
    <span
      className="inline-flex items-center gap-1.5"
      style={{ color: fresh ? "var(--pass)" : "var(--partial)" }}
    >
      <Icon size={16} aria-hidden />
      {fresh ? "Fresh" : "Stale"}
    </span>
  );
}

const columns: Column<EvidenceItem>[] = [
  {
    key: "id",
    header: "ID",
    render: (e) => <span className="font-mono">{e.id}</span>,
    sortValue: (e) => e.id,
  },
  { key: "title", header: "Evidence", render: (e) => e.title, sortValue: (e) => e.title },
  {
    key: "source",
    header: "Source",
    render: (e) => SOURCE_LABEL[e.source],
    sortValue: (e) => e.source,
  },
  {
    key: "collected",
    header: "Collected",
    render: (e) => <span className="tabular">{e.collected_at}</span>,
    sortValue: (e) => e.collected_at,
  },
  {
    key: "fresh",
    header: "Freshness",
    render: (e) => <Freshness fresh={e.fresh} />,
    sortValue: (e) => (e.fresh ? 0 : 1),
  },
];

export function EvidenceView() {
  return (
    <ListView<EvidenceItem>
      path="/evidence"
      caption="Evidence"
      columns={columns}
      rowKey={(e) => e.id}
      emptyMessage="No evidence from this source yet."
      filters={[
        {
          name: "source",
          label: "Source",
          options: Object.entries(SOURCE_LABEL).map(([value, label]) => ({ value, label })),
        },
      ]}
      detailTitle={(e) => e.id}
      renderDetail={(e) => (
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="text-muted">Evidence</dt>
            <dd className="font-medium">{e.title}</dd>
          </div>
          <div>
            <dt className="text-muted">Source</dt>
            <dd>{SOURCE_LABEL[e.source]}</dd>
          </div>
          <div>
            <dt className="text-muted">Collected</dt>
            <dd>{e.collected_at}</dd>
          </div>
          <div>
            <dt className="text-muted">Freshness</dt>
            <dd>
              <Freshness fresh={e.fresh} />
            </dd>
          </div>
        </dl>
      )}
    />
  );
}
