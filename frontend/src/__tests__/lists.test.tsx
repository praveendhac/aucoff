import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { ControlsView } from "@/components/lists/controls-view";
import { FindingsView, type Finding } from "@/components/lists/findings-view";
import { DataTable } from "@/components/table/data-table";

afterEach(() => vi.unstubAllGlobals());

const f = (id: string, severity: Finding["severity"], age: number): Finding => ({
  id,
  title: `Title ${id}`,
  severity,
  status: "open",
  framework_id: "soc2-2017",
  control_id: "UC-DEMO-001",
  first_seen: "2026-09-01",
  age_days: age,
});

function page(items: unknown[], next: string | null, source = "synthetic") {
  return new Response(JSON.stringify({ items, next_cursor: next, data_source: source }), {
    status: 200,
  });
}

test("the table sorts a column and announces it", () => {
  const rows = [f("F-2", "low", 5), f("F-1", "critical", 90)];
  render(
    <DataTable
      caption="Findings"
      rows={rows}
      rowKey={(r) => r.id}
      density="comfortable"
      columns={[
        { key: "id", header: "ID", render: (r) => r.id, sortValue: (r) => r.id },
        { key: "age", header: "Age", render: (r) => r.age_days, sortValue: (r) => r.age_days },
      ]}
    />,
  );
  const firstId = () => within(screen.getAllByRole("row")[1]).getAllByRole("cell")[0].textContent;
  expect(firstId()).toBe("F-2");
  fireEvent.click(screen.getByRole("button", { name: /ID/ }));
  expect(screen.getByRole("columnheader", { name: /ID/ })).toHaveAttribute(
    "aria-sort",
    "ascending",
  );
  expect(firstId()).toBe("F-1");
  fireEvent.click(screen.getByRole("button", { name: /ID/ }));
  expect(firstId()).toBe("F-2");
});

test("findings load through the BFF, are labelled demo data, page on request and open a drawer", async () => {
  const fetchMock = vi
    .fn()
    .mockResolvedValueOnce(page([f("F-1", "critical", 90)], "abc"))
    .mockResolvedValueOnce(page([f("F-2", "low", 5)], null));
  vi.stubGlobal("fetch", fetchMock);
  render(<FindingsView />);
  expect(await screen.findByRole("note")).toHaveTextContent(/Demo data/);
  expect(within(screen.getByRole("table")).getByText("Critical")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Load more" }));
  expect(await screen.findByText("F-2")).toBeInTheDocument();
  expect(String(fetchMock.mock.calls[1][0])).toContain("cursor=abc");
  expect(String(fetchMock.mock.calls[0][0])).toMatch(/^\/bff\/findings\?/);
  expect(screen.getByText("End of list")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "F-1" }));
  expect(screen.getByRole("dialog", { name: "F-1" })).toBeInTheDocument();
  fireEvent.keyDown(window, { key: "Escape" });
  await waitFor(() => expect(screen.queryByRole("dialog")).toBeNull());
});

test("choosing a filter reloads with the filter in the request", async () => {
  const fetchMock = vi.fn().mockImplementation(async () => page([f("F-1", "critical", 90)], null));
  vi.stubGlobal("fetch", fetchMock);
  render(<FindingsView />);
  await screen.findByText("F-1");
  fireEvent.change(screen.getByLabelText("Severity"), { target: { value: "critical" } });
  await waitFor(() =>
    expect(String(fetchMock.mock.calls.at(-1)?.[0])).toContain("severity=critical"),
  );
});

test("an empty real catalogue explains how to fill it and shows no demo banner", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(page([], null, "catalogue")));
  render(<ControlsView />);
  expect(await screen.findByText(/catalogue is empty/)).toBeInTheDocument();
  expect(screen.queryByRole("note")).toBeNull();
});

test("a 403 shows an explanation", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("{}", { status: 403 })));
  render(<FindingsView />);
  expect(await screen.findByRole("alert")).toHaveTextContent(/does not include access/);
});
