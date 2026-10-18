"use client";

import { ArrowDown, ArrowUp, ChevronsUpDown } from "lucide-react";
import { useMemo, useState } from "react";
import type { Density } from "@/lib/density";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => React.ReactNode;
  /** Present = the column can be sorted. */
  sortValue?: (row: T) => string | number;
}

export function DataTable<T>({
  caption,
  rows,
  columns,
  rowKey,
  density,
  onRowOpen,
}: {
  caption: string;
  rows: T[];
  columns: Column<T>[];
  rowKey: (row: T) => string;
  density: Density;
  onRowOpen?: (row: T) => void;
}) {
  const [sort, setSort] = useState<{ key: string; dir: "asc" | "desc" } | null>(null);

  const sorted = useMemo(() => {
    const col = columns.find((c) => c.key === sort?.key);
    if (!sort || !col?.sortValue) return rows;
    const get = col.sortValue;
    const factor = sort.dir === "asc" ? 1 : -1;
    return [...rows].sort((a, b) => {
      const x = get(a);
      const y = get(b);
      return (x < y ? -1 : x > y ? 1 : 0) * factor;
    });
  }, [rows, columns, sort]);

  const pad = density === "compact" ? "py-1.5" : "py-3.5"; // 36 px / 48 px rows (design.md 10.4)

  return (
    <div className="overflow-x-auto rounded-card border border-border-subtle">
      <table className="w-full text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="bg-surface text-left text-xs text-muted">
          <tr>
            {columns.map((c) => {
              const active = sort?.key === c.key;
              return (
                <th
                  key={c.key}
                  scope="col"
                  aria-sort={
                    active ? (sort?.dir === "asc" ? "ascending" : "descending") : undefined
                  }
                  className="px-4 py-2.5 font-medium"
                >
                  {c.sortValue ? (
                    <button
                      type="button"
                      className="inline-flex items-center gap-1 hover:text-text"
                      onClick={() =>
                        setSort(
                          active && sort?.dir === "asc"
                            ? { key: c.key, dir: "desc" }
                            : { key: c.key, dir: "asc" },
                        )
                      }
                    >
                      {c.header}
                      {active ? (
                        sort?.dir === "asc" ? (
                          <ArrowUp size={14} aria-hidden />
                        ) : (
                          <ArrowDown size={14} aria-hidden />
                        )
                      ) : (
                        <ChevronsUpDown size={14} aria-hidden />
                      )}
                    </button>
                  ) : (
                    c.header
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={rowKey(row)} className="border-t border-border-subtle hover:bg-surface">
              {columns.map((c, i) => (
                <td key={c.key} className={`px-4 ${pad}`}>
                  {i === 0 && onRowOpen ? (
                    <button
                      type="button"
                      className="text-left font-medium text-brand hover:underline"
                      onClick={() => onRowOpen(row)}
                    >
                      {c.render(row)}
                    </button>
                  ) : (
                    c.render(row)
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
