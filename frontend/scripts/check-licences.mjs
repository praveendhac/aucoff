// Licence gate for npm dependencies (constitution LIC-1, LIC-2, LIC-5).
// Fails on disallowed or unknown licences. PENDING_OWNER licences are permissive-style but not on the
// constitution's allow-list yet; they pass with a notice until the owner decides (see LICENCES.md).
import { execFileSync } from "node:child_process";

const ALLOWED = new Set([
  "MIT",
  "Apache-2.0",
  "BSD-2-Clause",
  "BSD-3-Clause",
  "ISC",
  "MPL-2.0",
  "PostgreSQL",
  "OFL-1.1",
]);
const PENDING_OWNER = new Set([
  "BlueOak-1.0.0",
  "0BSD",
  "CC0-1.0",
  "CC-BY-3.0",
  "CC-BY-4.0",
  "Python-2.0",
  "PSF-2.0",
  "MIT-0",
]);
const DENIED = /agpl|\bgpl|lgpl|sspl|busl|business source|commons clause/i;

const out = execFileSync(
  "npx",
  ["license-checker-rseidelsohn", "--json", "--excludePrivatePackages"],
  { encoding: "utf8", maxBuffer: 64 * 1024 * 1024 },
);
const pkgs = JSON.parse(out);

function terms(expr) {
  return expr
    .replace(/[()*]/g, "")
    .split(/\s+OR\s+/)
    .map((alt) =>
      alt
        .split(/\s+AND\s+/)
        .map((t) => t.trim())
        .filter(Boolean),
    );
}

const bad = [];
const pending = new Map();
for (const [name, info] of Object.entries(pkgs)) {
  const raw = Array.isArray(info.licenses) ? info.licenses.join(" AND ") : String(info.licenses);
  if (DENIED.test(raw)) {
    bad.push([name, raw]);
    continue;
  }
  const alts = terms(raw);
  const pass = alts.some((ts) => ts.every((t) => ALLOWED.has(t)));
  const passPending = alts.some((ts) => ts.every((t) => ALLOWED.has(t) || PENDING_OWNER.has(t)));
  if (pass) continue;
  if (passPending) pending.set(raw, [...(pending.get(raw) ?? []), name]);
  else bad.push([name, raw]);
}
if (pending.size) {
  console.warn("Pending owner approval (permissive-style, not yet on the allow-list):");
  for (const [lic, names] of pending)
    console.warn(`  ${lic}: ${names.length} package(s), e.g. ${names.slice(0, 2).join(", ")}`);
}
if (bad.length) {
  console.error("Disallowed or unknown licences (constitution LIC-1/LIC-2):");
  for (const [n, l] of bad) console.error(`  ${n}: ${l}`);
  process.exit(1);
}
console.log(`licence check passed (${Object.keys(pkgs).length} packages)`);
