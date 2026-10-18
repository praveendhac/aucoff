"use client";

import { Info, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import type { PostureDashboard } from "@/lib/dashboard";
import { KpiStrip } from "./kpi-strip";
import { FrameworkCoverage, SeverityComparison, StatusDistribution } from "./panels";

type State =
  | { kind: "loading" }
  | { kind: "error"; message: string }
  | { kind: "ready"; data: PostureDashboard };

// Loads through the BFF (/bff/*): the browser never holds an access token.
export function PostureDashboardView() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    fetch("/bff/dashboards/posture", { headers: { Accept: "application/json" } })
      .then(async (r) => {
        if (r.status === 403) throw new Error("Your role does not include dashboard access.");
        if (!r.ok) throw new Error(`The dashboard could not be loaded (status ${r.status}).`);
        return (await r.json()) as PostureDashboard;
      })
      .then((data) => !cancelled && setState({ kind: "ready", data }))
      .catch((e: Error) => !cancelled && setState({ kind: "error", message: e.message }));
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading") {
    return (
      <p role="status" className="text-muted">
        Loading dashboard…
      </p>
    );
  }
  if (state.kind === "error") {
    return (
      <div
        role="alert"
        className="flex items-start gap-3 rounded-card border border-border-subtle bg-surface p-5"
      >
        <TriangleAlert size={20} aria-hidden style={{ color: "var(--partial)" }} />
        <p>{state.message}</p>
      </div>
    );
  }
  const { data } = state;
  return (
    <div className="space-y-6">
      {data.data_source === "synthetic" ? (
        <div
          role="note"
          className="flex items-start gap-3 rounded-card p-4 text-sm font-medium"
          style={{ background: "var(--partial-tint)", color: "var(--partial)" }}
        >
          <Info size={18} aria-hidden />
          <p>
            Demo data. These numbers are synthetic and are not real compliance results; real figures
            appear after the first assessment runs.
          </p>
        </div>
      ) : null}
      <KpiStrip kpis={data.kpis} />
      <div className="grid gap-6 xl:grid-cols-2">
        <FrameworkCoverage rows={data.frameworks} />
        <StatusDistribution data={data.status_distribution} />
      </div>
      <SeverityComparison rows={data.severity_comparison} />
    </div>
  );
}
