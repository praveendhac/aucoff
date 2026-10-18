import type { NextRequest } from "next/server";
import { requireSession, unauthorised } from "@/lib/session";

// Backend-for-frontend proxy: the browser never holds an access token. This handler checks the
// session, then forwards the call to the FastAPI gateway with the user's token as a bearer token.
const BACKEND = process.env.BACKEND_URL ?? "https://aucoff-backend:8000";
const FORWARDED_REQUEST_HEADERS = ["content-type", "accept", "if-none-match"];

async function forward(request: NextRequest, ctx: { params: Promise<{ path: string[] }> }) {
  const token = await requireSession(request);
  if (!token) return unauthorised();

  const { path } = await ctx.params;
  if (path.some((segment) => segment === ".." || segment === "." || segment === "")) {
    return Response.json({ title: "Bad request", status: 400 }, { status: 400 });
  }
  const target = new URL(`${BACKEND}/api/v1/${path.map(encodeURIComponent).join("/")}`);
  target.search = request.nextUrl.search;

  const headers = new Headers();
  for (const name of FORWARDED_REQUEST_HEADERS) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  headers.set("authorization", `Bearer ${token.accessToken}`);

  const hasBody = !["GET", "HEAD"].includes(request.method);
  const upstream = await fetch(target, {
    method: request.method,
    headers,
    body: hasBody ? await request.arrayBuffer() : undefined,
    redirect: "manual",
  });
  const response = new Response(upstream.body, { status: upstream.status });
  for (const name of ["content-type", "cache-control", "www-authenticate"]) {
    const value = upstream.headers.get(name);
    if (value) response.headers.set(name, value);
  }
  return response;
}

export { forward as GET, forward as POST, forward as PUT, forward as PATCH, forward as DELETE };
