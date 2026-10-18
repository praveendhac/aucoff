// Authentication-everywhere guard for the web app (constitution ZT-1, ZT-2, ZT-8).
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";
import { beforeEach, expect, test, vi } from "vitest";
import { isPublicPath } from "@/lib/public-paths";

vi.mock("next-auth/jwt", () => ({ getToken: vi.fn() }));
import { getToken } from "next-auth/jwt";

const APP = join(process.cwd(), "src", "app");

function routeFiles(dir: string): string[] {
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    if (statSync(full).isDirectory()) return routeFiles(full);
    return /^route\.(ts|tsx|js)$/.test(name) ? [full] : [];
  });
}

test("only the OIDC handlers are public paths", () => {
  expect(isPublicPath("/login")).toBe(true);
  expect(isPublicPath("/api/auth/callback/keycloak")).toBe(true);
  expect(isPublicPath("/_next/static/chunk.js")).toBe(true);
  for (const path of [
    "/",
    "/bff/health",
    "/api/v1/health",
    "/api/authx",
    "/dashboard",
    "/login/x",
  ]) {
    expect(isPublicPath(path), path).toBe(false);
  }
});

test("every route handler outside /api/auth checks the session first", () => {
  const offenders = routeFiles(APP)
    .map((file) => relative(APP, file))
    .filter((file) => !file.startsWith(join("api", "auth")))
    .filter((file) => !readFileSync(join(APP, file), "utf8").includes("requireSession("));
  expect(offenders).toEqual([]);
});

beforeEach(() => vi.mocked(getToken).mockReset());

test("the BFF proxy refuses a request without a session", async () => {
  vi.mocked(getToken).mockResolvedValue(null);
  const { GET } = await import("@/app/bff/[...path]/route");
  const { NextRequest } = await import("next/server");
  const response = await GET(new NextRequest("http://x/bff/health"), {
    params: Promise.resolve({ path: ["health"] }),
  });
  expect(response.status).toBe(401);
});

test("the BFF proxy refuses a session whose refresh failed", async () => {
  vi.mocked(getToken).mockResolvedValue({ accessToken: "t", error: "RefreshFailed" });
  const { GET } = await import("@/app/bff/[...path]/route");
  const { NextRequest } = await import("next/server");
  const response = await GET(new NextRequest("http://x/bff/health"), {
    params: Promise.resolve({ path: ["health"] }),
  });
  expect(response.status).toBe(401);
});

test("the BFF proxy forwards with the user's bearer token and rejects path tricks", async () => {
  vi.mocked(getToken).mockResolvedValue({ accessToken: "user-token" });
  const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
  vi.stubGlobal("fetch", fetchMock);
  const { GET } = await import("@/app/bff/[...path]/route");
  const { NextRequest } = await import("next/server");

  const ok = await GET(new NextRequest("http://x/bff/health?a=1", { headers: { cookie: "s=1" } }), {
    params: Promise.resolve({ path: ["health"] }),
  });
  expect(ok.status).toBe(200);
  const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
  expect(url.pathname).toBe("/api/v1/health");
  expect(url.search).toBe("?a=1");
  const headers = init.headers as Headers;
  expect(headers.get("authorization")).toBe("Bearer user-token");
  expect(headers.get("cookie")).toBeNull();

  const bad = await GET(new NextRequest("http://x/bff/a"), {
    params: Promise.resolve({ path: ["..", "admin"] }),
  });
  expect(bad.status).toBe(400);
  vi.unstubAllGlobals();
});
