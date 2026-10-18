"use client";

import { Info, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { DetailDrawer } from "@/components/shell/detail-drawer";
import { useDensity } from "@/lib/density";
import { useCursorList } from "@/lib/use-list";
import { type Column, DataTable } from "./data-table";

export interface Filter {
  name: string;
  label: string;
  options: { value: string; label: string }[];
}

export function ListView<T>({
  path,
  caption,
  columns,
  rowKey,
  filters = [],
  detailTitle,
  renderDetail,
  emptyMessage,
}: {
  path: string;
  caption: string;
  columns: Column<T>[];
  rowKey: (row: T) => string;
  filters?: Filter[];
  detailTitle: (row: T) => string;
  renderDetail: (row: T) => React.ReactNode;
  emptyMessage: string;
}) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<T | null>(null);
  const [density, setDensity] = useDensity();
  const params = Object.fromEntries(Object.entries(values).filter(([, v]) => v !== ""));
  const { state, loadMore } = useCursorList<T>(path, params);

  return (
    <div className="space-y-4">
      {state.kind === "ready" && state.source === "synthetic" ? (
        <div
          role="note"
          className="flex items-start gap-3 rounded-card p-4 text-sm font-medium"
          style={{ background: "var(--partial-tint)", color: "var(--partial)" }}
        >
          <Info size={18} aria-hidden />
          <p>Demo data. These rows are synthetic and are not real results.</p>
        </div>
      ) : null}

      <div className="flex flex-wrap items-end gap-4">
        {filters.map((f) => (
          <label key={f.name} className="flex flex-col gap-1 text-xs text-muted">
            {f.label}
            <select
              value={values[f.name] ?? ""}
              onChange={(e) => setValues((v) => ({ ...v, [f.name]: e.target.value }))}
              className="rounded-control border border-border-control bg-bg px-3 py-1.5 text-sm text-text"
            >
              <option value="">All</option>
              {f.options.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        ))}
        <fieldset className="ml-auto flex items-center gap-2 text-xs text-muted">
          <legend className="sr-only">Row density</legend>
          {(["comfortable", "compact"] as const).map((d) => (
            <label key={d} className="flex items-center gap-1">
              <input
                type="radio"
                name="density"
                checked={density === d}
                onChange={() => setDensity(d)}
              />
              {d === "comfortable" ? "Comfortable" : "Compact"}
            </label>
          ))}
        </fieldset>
      </div>

      {state.kind === "loading" ? (
        <p role="status" className="text-muted">
          Loading…
        </p>
      ) : state.kind === "error" ? (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-card border border-border-subtle bg-surface p-5"
        >
          <TriangleAlert size={20} aria-hidden style={{ color: "var(--partial)" }} />
          <p>{state.message}</p>
        </div>
      ) : state.rows.length === 0 ? (
        <div className="rounded-card border border-dashed border-border-control p-10 text-center text-muted">
          {emptyMessage}
        </div>
      ) : (
        <>
          <DataTable
            caption={caption}
            rows={state.rows}
            columns={columns}
            rowKey={rowKey}
            density={density}
            onRowOpen={setSelected}
          />
          <div className="flex items-center justify-between text-xs text-muted">
            <span className="tabular">{state.rows.length} shown</span>
            {state.next ? (
              <button
                type="button"
                onClick={loadMore}
                disabled={state.loadingMore}
                className="rounded-control border border-border-control px-4 py-1.5 text-sm text-text hover:bg-surface disabled:opacity-60"
              >
                {state.loadingMore ? "Loading…" : "Load more"}
              </button>
            ) : (
              <span>End of list</span>
            )}
          </div>
        </>
      )}

      <DetailDrawer
        open={selected !== null}
        title={selected ? detailTitle(selected) : ""}
        onClose={() => setSelected(null)}
      >
        {selected ? renderDetail(selected) : null}
      </DetailDrawer>
    </div>
  );
}
