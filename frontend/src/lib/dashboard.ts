// Shape of GET /api/v1/dashboards/posture (backend/openapi.yaml, API-70).
export interface Kpi {
  value: number;
  delta_vs_previous: number;
}
export interface PostureDashboard {
  data_source: "synthetic" | "assessments";
  kpis: {
    posture_score: Kpi;
    coverage_pct: Kpi;
    open_findings: Kpi;
    pending_approvals: Kpi;
    evidence_freshness_pct: Kpi;
  };
  status_distribution: {
    pass: number;
    partial: number;
    fail: number;
    unknown: number;
    not_applicable: number;
  };
  severity_comparison: {
    severity: "critical" | "high" | "medium" | "low";
    latest: number;
    previous: number;
    before_previous: number;
  }[];
  frameworks: {
    framework_id: string;
    name: string;
    coverage_pct: number;
    delta_vs_previous: number;
  }[];
}

/** For counts (findings, approvals) a decrease is good; for percentages and scores an increase is. */
export function deltaTone(delta: number, lowerIsBetter: boolean): "better" | "worse" | "same" {
  if (delta === 0) return "same";
  return delta < 0 === lowerIsBetter ? "better" : "worse";
}
