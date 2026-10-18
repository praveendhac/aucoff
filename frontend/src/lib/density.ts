"use client";

import { useSyncExternalStore } from "react";

export type Density = "comfortable" | "compact";
const KEY = "aucoff-density";
const EVENT = "aucoff-density-change";

function read(): Density {
  try {
    return localStorage.getItem(KEY) === "compact" ? "compact" : "comfortable";
  } catch {
    return "comfortable"; // storage blocked: fall back to the default
  }
}

function subscribe(onChange: () => void): () => void {
  window.addEventListener(EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

export function useDensity(): [Density, (next: Density) => void] {
  const density = useSyncExternalStore<Density>(subscribe, read, () => "comfortable");
  function set(next: Density) {
    try {
      localStorage.setItem(KEY, next);
    } catch {
      // not persisted; the event below still updates this page
    }
    window.dispatchEvent(new Event(EVENT));
  }
  return [density, set];
}
