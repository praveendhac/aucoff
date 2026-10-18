import { getToken } from "next-auth/jwt";
import type { NextRequest } from "next/server";

// Every route handler outside /api/auth must start with this check (ZT-1, ZT-2); the proxy
// repeats it for pages, so a handler never relies on the proxy alone.
export async function requireSession(request: NextRequest) {
  const token = await getToken({ req: request });
  if (!token?.accessToken || token.error) return null;
  return token;
}

export function unauthorised(): Response {
  return Response.json(
    { type: "about:blank", title: "Authentication required", status: 401 },
    { status: 401, headers: { "Content-Type": "application/problem+json" } },
  );
}
