// The ONLY paths reachable without a session (constitution ZT-2): the OIDC login/callback/logout
// handlers (Auth.js), the login page, and static shell assets that contain no tenant data.
const PUBLIC_EXACT = new Set(["/login", "/favicon.ico"]);
const PUBLIC_PREFIXES = ["/api/auth/", "/_next/static/", "/_next/image"];

export function isPublicPath(pathname: string): boolean {
  return PUBLIC_EXACT.has(pathname) || PUBLIC_PREFIXES.some((p) => pathname.startsWith(p));
}
