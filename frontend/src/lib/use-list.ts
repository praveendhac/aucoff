"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

export interface Page<T> {
  items: T[];
  next_cursor: string | null;
  data_source: "synthetic" | "catalogue" | "assessments";
}

type Loaded<T> =
  | { kind: "error"; message: string; rows: T[] }
  | {
      kind: "ready";
      rows: T[];
      next: string | null;
      source: Page<T>["data_source"];
      loadingMore: boolean;
    };
type State<T> = { kind: "loading"; rows: T[] } | Loaded<T>;
type Keyed<T> = { key: string; value: Loaded<T> };

// Loads a cursor-paginated list through the BFF (/bff/*): the browser never holds a token.
export function useCursorList<T>(path: string, params: Record<string, string>) {
  const [result, setResult] = useState<Keyed<T> | null>(null);
  const key = JSON.stringify([path, params]);
  // A result for different filters is stale: show loading until the new one arrives.
  const state = useMemo<State<T>>(
    () => (result && result.key === key ? result.value : { kind: "loading", rows: [] }),
    [result, key],
  );
  const generation = useRef(0);

  const fetchPage = useCallback(
    async (cursor: string | null): Promise<Page<T>> => {
      const q = new URLSearchParams({ limit: "25", ...params });
      if (cursor) q.set("cursor", cursor);
      const r = await fetch(`/bff${path}?${q}`, { headers: { Accept: "application/json" } });
      if (r.status === 403) throw new Error("Your role does not include access to this list.");
      if (!r.ok) throw new Error(`The list could not be loaded (status ${r.status}).`);
      return (await r.json()) as Page<T>;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [key],
  );

  useEffect(() => {
    const mine = ++generation.current;
    fetchPage(null)
      .then((p) => {
        if (mine === generation.current)
          setResult({
            key,
            value: {
              kind: "ready",
              rows: p.items,
              next: p.next_cursor,
              source: p.data_source,
              loadingMore: false,
            },
          });
      })
      .catch((e: Error) => {
        if (mine === generation.current)
          setResult({ key, value: { kind: "error", message: e.message, rows: [] } });
      });
  }, [fetchPage, key]);

  const loadMore = useCallback(() => {
    if (state.kind !== "ready" || !state.next || state.loadingMore) return;
    const mine = generation.current;
    const { rows, next } = state;
    setResult({ key, value: { ...state, loadingMore: true } });
    fetchPage(next)
      .then((p) => {
        if (mine !== generation.current) return;
        setResult({
          key,
          value: {
            kind: "ready",
            rows: [...rows, ...p.items],
            next: p.next_cursor,
            source: p.data_source,
            loadingMore: false,
          },
        });
      })
      .catch((e: Error) => {
        if (mine === generation.current)
          setResult({ key, value: { kind: "error", message: e.message, rows } });
      });
  }, [fetchPage, key, state]);

  return { state, loadMore };
}
