// Automated WCAG check of the design tokens (design.md section 10.2, section 13).
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { expect, test } from "vitest";
import { contrast } from "@/lib/contrast";
import { brand, severity, status, surfaces, type Theme } from "@/lib/tokens";

const themes: Theme[] = ["light", "dark"];

test.each(themes)("%s: text, brand and accent colours meet WCAG AA", (t) => {
  const s = surfaces[t];
  const b = brand[t];
  expect(contrast(s.text, s.bg)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(s["text-muted"], s.bg)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(s["text-muted"], s.surface)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(b.brand, s.bg)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(b.teal, s.bg)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(b.deep, s.bg)).toBeGreaterThanOrEqual(4.5);
  expect(contrast(b.onBrand, b.brand)).toBeGreaterThanOrEqual(4.5);
  // UI component borders need 3:1 against the page background
  expect(contrast(s["border-control"], s.bg)).toBeGreaterThanOrEqual(3);
});

test.each(themes)("%s: every status is legible on the page and on its own tint", (t) => {
  for (const [key, c] of Object.entries(status[t])) {
    expect(contrast(c.fg, surfaces[t].bg), `${key} on bg`).toBeGreaterThanOrEqual(4.5);
    expect(contrast(c.fg, c.tint), `${key} on tint`).toBeGreaterThanOrEqual(4.5);
  }
});

test.each(themes)("%s: every severity colour is legible on the page and the card surface", (t) => {
  for (const [key, hex] of Object.entries(severity[t])) {
    expect(contrast(hex, surfaces[t].bg), `${key} on bg`).toBeGreaterThanOrEqual(4.5);
    expect(contrast(hex, surfaces[t].surface), `${key} on surface`).toBeGreaterThanOrEqual(4.5);
  }
});

test("globals.css repeats exactly the token values", () => {
  const css = readFileSync(join(process.cwd(), "src", "app", "globals.css"), "utf8").toLowerCase();
  const values: string[] = [];
  for (const t of themes) {
    values.push(
      ...Object.values(surfaces[t]),
      ...Object.values(brand[t]),
      ...Object.values(severity[t]),
    );
    for (const c of Object.values(status[t])) values.push(c.fg, c.tint);
  }
  const missing = [...new Set(values)].filter((hex) => !css.includes(hex.toLowerCase()));
  expect(missing).toEqual([]);
});
