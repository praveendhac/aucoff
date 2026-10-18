import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { PostureDashboardView } from "@/components/dashboard/posture-dashboard";
import { Sidebar } from "@/components/shell/sidebar";
import { StatusBadge, SeverityLabel } from "@/components/status";
import { deltaTone, type PostureDashboard } from "@/lib/dashboard";
import { navFor } from "@/lib/nav";

vi.mock("next/navigation", () => ({ usePathname: () => "/" }));

afterEach(() => vi.unstubAllGlobals());

const labels = (roles: string[]) => navFor(roles).map((i) => i.label);

test("navigation is filtered by role", () => {
  expect(labels(["admin"])).toContain("Settings");
  expect(labels(["admin"])).toContain("Audit log");
  expect(labels(["auditor"])).toEqual([
    "Dashboard",
    "Controls",
    "Evidence",
    "Reports",
    "Audit log",
  ]);
  expect(labels(["executive"])).toEqual(["Dashboard", "Reports"]);
  expect(labels(["engineer"])).not.toContain("Settings");
  expect(labels([])).toEqual(["Dashboard"]);
});

test("unbuilt sections are shown disabled, not as broken links", () => {
  render(<Sidebar items={navFor(["ciso"])} collapsed={false} onToggle={() => {}} />);
  expect(screen.getByRole("link", { name: "Dashboard" })).toHaveAttribute("aria-current", "page");
  expect(screen.queryByRole("link", { name: /Assessments/ })).toBeNull();
  expect(screen.getByText("Assessments").closest("[aria-disabled]")).not.toBeNull();
});

test("status and severity always show an icon and a text label", () => {
  const { container } = render(
    <>
      <StatusBadge status="fail" />
      <SeverityLabel severity="critical" />
    </>,
  );
  expect(screen.getByText("Fail")).toBeInTheDocument();
  expect(screen.getByText("Critical")).toBeInTheDocument();
  expect(container.querySelectorAll("svg").length).toBe(2);
});

test("delta tone depends on whether lower is better", () => {
  expect(deltaTone(-6, true)).toBe("better");
  expect(deltaTone(2, true)).toBe("worse");
  expect(deltaTone(2, false)).toBe("better");
  expect(deltaTone(0, false)).toBe("same");
});

const demo: PostureDashboard = {
  data_source: "synthetic",
  kpis: {
    posture_score: { value: 78.4, delta_vs_previous: 2.1 },
    coverage_pct: { value: 86, delta_vs_previous: 3.5 },
    open_findings: { value: 42, delta_vs_previous: -6 },
    pending_approvals: { value: 7, delta_vs_previous: 2 },
    evidence_freshness_pct: { value: 91.2, delta_vs_previous: -1.4 },
  },
  status_distribution: { pass: 312, partial: 64, fail: 38, unknown: 21, not_applicable: 15 },
  severity_comparison: [
    { severity: "critical", latest: 2, previous: 4, before_previous: 5 },
    { severity: "high", latest: 9, previous: 12, before_previous: 11 },
    { severity: "medium", latest: 17, previous: 16, before_previous: 19 },
    { severity: "low", latest: 14, previous: 15, before_previous: 18 },
  ],
  frameworks: [
    { framework_id: "soc2-2017", name: "SOC 2", coverage_pct: 91, delta_vs_previous: 2 },
  ],
};

test("the dashboard says plainly that demo data is not real", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(new Response(JSON.stringify(demo), { status: 200 })),
  );
  render(<PostureDashboardView />);
  expect(await screen.findByRole("note")).toHaveTextContent(/Demo data/);
  expect(screen.getByText("78.4")).toBeInTheDocument();
  expect(screen.getByRole("progressbar", { name: "SOC 2 coverage" })).toHaveAttribute(
    "aria-valuenow",
    "91",
  );
  expect(fetch).toHaveBeenCalledWith("/bff/dashboards/posture", expect.anything());
});

test("a role without dashboard access sees an explanation, not a crash", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 403 })));
  render(<PostureDashboardView />);
  await waitFor(() =>
    expect(screen.getByRole("alert")).toHaveTextContent(/does not include dashboard access/),
  );
});
